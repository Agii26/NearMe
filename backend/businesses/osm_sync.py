"""
Core logic for pulling business data from OpenStreetMap's Overpass API and
upserting it into our Business table. Split from the management command
itself so the parsing/upsert logic can be unit tested without a real network
call — see businesses/tests/test_sync_osm_businesses.py.
"""

import requests
from django.contrib.gis.geos import Point

from categories.models import Category

from .osm_category_map import resolve_category_slug
from .osm_hours import parse_opening_hours
from .models import Business

OVERPASS_QUERY_TEMPLATE = """
[out:json][timeout:60];
(
  node["shop"]({south},{west},{north},{east});
  node["amenity"]({south},{west},{north},{east});
  way["shop"]({south},{west},{north},{east});
  way["amenity"]({south},{west},{north},{east});
);
out center tags;
"""


def build_query(bbox):
    south, west, north, east = bbox
    return OVERPASS_QUERY_TEMPLATE.format(
        south=south, west=west, north=north, east=east
    )


def fetch_overpass_elements(bbox, api_url, timeout=60):
    """Makes the real HTTP call to Overpass. Mocked out in tests."""
    query = build_query(bbox)
    response = requests.post(api_url, data={"data": query}, timeout=timeout)
    response.raise_for_status()
    return response.json().get("elements", [])


def _extract_address(tags):
    parts = [
        tags.get("addr:housenumber", ""),
        tags.get("addr:street", ""),
    ]
    street_line = " ".join(p for p in parts if p).strip()
    city = tags.get("addr:city", "")
    pieces = [p for p in [street_line, city] if p]
    return ", ".join(pieces)


def build_business_fields(element):
    """
    Given one Overpass element dict, returns (osm_id, defaults_dict) ready
    for Business.objects.update_or_create(osm_id=osm_id, defaults=defaults),
    or None if the element should be skipped (no name, no coordinates, or
    no tag we recognize in our category map).
    """
    tags = element.get("tags", {})
    name = tags.get("name")
    if not name:
        return None

    category_slug = resolve_category_slug(tags)
    if category_slug is None:
        return None

    lat = element.get("lat")
    lon = element.get("lon")
    if lat is None or lon is None:
        center = element.get("center") or {}
        lat, lon = center.get("lat"), center.get("lon")
    if lat is None or lon is None:
        return None

    try:
        category = Category.objects.get(slug=category_slug)
    except Category.DoesNotExist:
        return None

    raw_hours = tags.get("opening_hours", "")
    parsed_hours = parse_opening_hours(raw_hours) if raw_hours else None

    osm_id = f"{element['type']}/{element['id']}"
    defaults = {
        "name": name,
        "category": category,
        "location": Point(float(lon), float(lat)),
        "address": _extract_address(tags),
        "hours": parsed_hours,
        "raw_hours_text": raw_hours[:255],
        "contact_phone": tags.get("phone", tags.get("contact:phone", ""))[:50],
        "contact_email": tags.get("email", tags.get("contact:email", ""))[:254],
    }
    return osm_id, defaults


def sync_businesses(bbox, api_url):
    """
    Runs one full sync pass. Returns a dict of counts. Idempotent: re-running
    with the same data updates existing rows (matched on osm_id) rather than
    duplicating them, since update_or_create matches on osm_id first.
    """
    elements = fetch_overpass_elements(bbox, api_url)
    counts = {"created": 0, "updated": 0, "skipped": 0, "total_fetched": len(elements)}

    for element in elements:
        result = build_business_fields(element)
        if result is None:
            counts["skipped"] += 1
            continue
        osm_id, defaults = result
        _, created = Business.objects.update_or_create(osm_id=osm_id, defaults=defaults)
        counts["created" if created else "updated"] += 1

    return counts

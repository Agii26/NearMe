"""
Maps OpenStreetMap `shop=*` and `amenity=*` tag values to our internal
Category slugs (see categories/migrations/0002_seed_categories.py).

Elements whose tags aren't in this map are skipped by the sync command
rather than dumped into a catch-all bucket — a smaller, correctly
categorized dataset is more useful than a larger, mis-labeled one.
"""

SHOP_TAG_TO_SLUG = {
    "supermarket": "grocery",
    "convenience": "grocery",
    "greengrocer": "grocery",
    "bakery": "grocery",
    "butcher": "grocery",
    "clothes": "retail",
    "shoes": "retail",
    "jewelry": "retail",
    "electronics": "retail",
    "books": "retail",
    "florist": "retail",
    "gift": "retail",
    "furniture": "retail",
    "hardware": "retail",
    "stationery": "retail",
    "mobile_phone": "retail",
    "hairdresser": "beauty-personal-care",
    "beauty": "beauty-personal-care",
    "massage": "beauty-personal-care",
    "car_repair": "automotive",
    "car": "automotive",
    "laundry": "home-services",
    "dry_cleaning": "home-services",
}

AMENITY_TAG_TO_SLUG = {
    "restaurant": "food-dining",
    "cafe": "food-dining",
    "fast_food": "food-dining",
    "bar": "food-dining",
    "pub": "food-dining",
    "food_court": "food-dining",
    "pharmacy": "health-wellness",
    "clinic": "health-wellness",
    "dentist": "health-wellness",
    "hospital": "health-wellness",
    "veterinary": "health-wellness",
    "bank": "professional-services",
    "fuel": "automotive",
    "car_wash": "automotive",
}


def resolve_category_slug(tags):
    """Given an OSM element's tags dict, return the matching Category slug or None."""
    if "shop" in tags and tags["shop"] in SHOP_TAG_TO_SLUG:
        return SHOP_TAG_TO_SLUG[tags["shop"]]
    if "amenity" in tags and tags["amenity"] in AMENITY_TAG_TO_SLUG:
        return AMENITY_TAG_TO_SLUG[tags["amenity"]]
    return None

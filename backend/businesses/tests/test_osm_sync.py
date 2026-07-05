from django.test import TestCase

from categories.models import Category
from businesses.osm_sync import build_business_fields


class BuildBusinessFieldsTests(TestCase):
    def setUp(self):
        self.food_category = Category.objects.get(slug="food-dining")

    def test_node_with_recognized_amenity_tag(self):
        element = {
            "type": "node",
            "id": 12345,
            "lat": 14.6507,
            "lon": 121.0494,
            "tags": {
                "amenity": "cafe",
                "name": "Better Days Café",
                "addr:housenumber": "42",
                "addr:street": "Maginhawa St",
                "addr:city": "Quezon City",
                "phone": "0917 123 4567",
                "opening_hours": "Mo-Fr 08:00-21:00",
            },
        }
        result = build_business_fields(element)
        self.assertIsNotNone(result)
        osm_id, defaults = result
        self.assertEqual(osm_id, "node/12345")
        self.assertEqual(defaults["name"], "Better Days Café")
        self.assertEqual(defaults["category"], self.food_category)
        self.assertEqual(defaults["address"], "42 Maginhawa St, Quezon City")
        self.assertEqual(defaults["contact_phone"], "0917 123 4567")
        self.assertEqual(defaults["hours"]["mon"], [["08:00", "21:00"]])
        self.assertAlmostEqual(defaults["location"].y, 14.6507)
        self.assertAlmostEqual(defaults["location"].x, 121.0494)

    def test_way_uses_center_coordinates(self):
        element = {
            "type": "way",
            "id": 999,
            "center": {"lat": 14.60, "lon": 121.02},
            "tags": {"shop": "supermarket", "name": "Corner Mart"},
        }
        result = build_business_fields(element)
        self.assertIsNotNone(result)
        osm_id, defaults = result
        self.assertEqual(osm_id, "way/999")
        self.assertAlmostEqual(defaults["location"].y, 14.60)

    def test_missing_name_is_skipped(self):
        element = {
            "type": "node",
            "id": 1,
            "lat": 14.6,
            "lon": 121.0,
            "tags": {"amenity": "cafe"},
        }
        self.assertIsNone(build_business_fields(element))

    def test_unrecognized_tag_is_skipped(self):
        element = {
            "type": "node",
            "id": 2,
            "lat": 14.6,
            "lon": 121.0,
            "tags": {"amenity": "place_of_worship", "name": "Some Chapel"},
        }
        self.assertIsNone(build_business_fields(element))

    def test_missing_coordinates_is_skipped(self):
        element = {
            "type": "way",
            "id": 3,
            "tags": {"shop": "bakery", "name": "No Coords Bakery"},
        }
        self.assertIsNone(build_business_fields(element))

    def test_unparseable_hours_falls_back_to_raw_text_only(self):
        element = {
            "type": "node",
            "id": 4,
            "lat": 14.6,
            "lon": 121.0,
            "tags": {
                "amenity": "restaurant",
                "name": "Mystery Hours Grill",
                "opening_hours": "PH off",
            },
        }
        _, defaults = build_business_fields(element)
        self.assertIsNone(defaults["hours"])
        self.assertEqual(defaults["raw_hours_text"], "PH off")

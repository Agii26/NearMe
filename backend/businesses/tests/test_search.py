from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase

from categories.models import Category
from businesses.models import Business

ORIGIN_LAT, ORIGIN_LNG = 14.650, 121.050


class BusinessSearchTests(APITestCase):
    def setUp(self):
        self.food = Category.objects.get(slug="food-dining")
        self.retail = Category.objects.get(slug="retail")

        self.near = Business.objects.create(
            name="Better Days Café",
            category=self.food,
            location=Point(ORIGIN_LNG, ORIGIN_LAT + 0.001),  # ~0.11 km away
        )
        self.mid = Business.objects.create(
            name="Kusina ni Aling Nena",
            category=self.food,
            location=Point(ORIGIN_LNG, ORIGIN_LAT + 0.01),  # ~1.1 km away
        )
        self.far = Business.objects.create(
            name="IronWorks Hardware",
            category=self.retail,
            location=Point(ORIGIN_LNG, ORIGIN_LAT + 0.06),  # ~6.7 km away
        )

    def test_requires_lat_and_lng(self):
        response = self.client.get("/api/businesses/search")
        self.assertEqual(response.status_code, 400)

    def test_rejects_out_of_range_coordinates(self):
        response = self.client.get("/api/businesses/search?lat=200&lng=121.05")
        self.assertEqual(response.status_code, 400)

    def test_default_radius_orders_by_distance_and_excludes_far_business(self):
        response = self.client.get(
            f"/api/businesses/search?lat={ORIGIN_LAT}&lng={ORIGIN_LNG}"
        )
        self.assertEqual(response.status_code, 200)
        names = [b["name"] for b in response.data["results"]]
        self.assertEqual(names, ["Better Days Café", "Kusina ni Aling Nena"])
        self.assertNotIn("IronWorks Hardware", names)

        # distance_km should be present and correctly ordered ascending
        distances = [b["distance_km"] for b in response.data["results"]]
        self.assertEqual(distances, sorted(distances))

    def test_larger_radius_includes_far_business(self):
        response = self.client.get(
            f"/api/businesses/search?lat={ORIGIN_LAT}&lng={ORIGIN_LNG}&radius=10"
        )
        names = [b["name"] for b in response.data["results"]]
        self.assertIn("IronWorks Hardware", names)

    def test_category_filter(self):
        response = self.client.get(
            f"/api/businesses/search?lat={ORIGIN_LAT}&lng={ORIGIN_LNG}&radius=10&category=retail"
        )
        names = [b["name"] for b in response.data["results"]]
        self.assertEqual(names, ["IronWorks Hardware"])

    def test_text_search_is_case_insensitive(self):
        response = self.client.get(
            f"/api/businesses/search?lat={ORIGIN_LAT}&lng={ORIGIN_LNG}&q=kusina"
        )
        names = [b["name"] for b in response.data["results"]]
        self.assertEqual(names, ["Kusina ni Aling Nena"])

    def test_radius_is_capped_at_max(self):
        # Even an absurd radius request shouldn't error or return everything
        # unbounded — it's capped server-side.
        response = self.client.get(
            f"/api/businesses/search?lat={ORIGIN_LAT}&lng={ORIGIN_LNG}&radius=99999"
        )
        self.assertEqual(response.status_code, 200)


class BusinessDetailTests(APITestCase):
    def setUp(self):
        self.food = Category.objects.get(slug="food-dining")
        self.business = Business.objects.create(
            name="Better Days Café",
            category=self.food,
            location=Point(ORIGIN_LNG, ORIGIN_LAT),
            address="42 Maginhawa St, Quezon City",
            contact_phone="0917 123 4567",
            hours={
                "mon": [["00:00", "24:00"]],
                "tue": [["00:00", "24:00"]],
                "wed": [["00:00", "24:00"]],
                "thu": [["00:00", "24:00"]],
                "fri": [["00:00", "24:00"]],
                "sat": [["00:00", "24:00"]],
                "sun": [["00:00", "24:00"]],
            },
        )

    def test_detail_returns_expected_fields(self):
        response = self.client.get(f"/api/businesses/{self.business.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Better Days Café")
        self.assertEqual(response.data["address"], "42 Maginhawa St, Quezon City")
        self.assertEqual(response.data["contact_phone"], "0917 123 4567")
        self.assertTrue(response.data["is_open_now"])  # open 24/7 in this fixture
        self.assertEqual(response.data["category"]["slug"], "food-dining")

    def test_detail_404_for_missing_business(self):
        response = self.client.get("/api/businesses/999999/")
        self.assertEqual(response.status_code, 404)

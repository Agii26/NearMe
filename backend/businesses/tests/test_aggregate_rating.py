from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase

from categories.models import Category
from businesses.models import Business
from reviews.models import Review

User = get_user_model()

ORIGIN_LAT, ORIGIN_LNG = 14.650, 121.050


class AggregateRatingTests(APITestCase):
    """
    Regression coverage for a real ORM footgun: annotating Avg/Count over a
    reverse FK (reviews) in the same queryset as other joins/filters can
    silently inflate counts or skew averages if not done carefully
    (Count needs distinct=True, Avg needs its own filter). These tests use
    3+ reviews specifically so a fan-out bug would actually show up as a
    wrong number, not just an off-by-one that's easy to miss with 1 review.
    """

    def setUp(self):
        self.category = Category.objects.get(slug="food-dining")
        self.business = Business.objects.create(
            name="Better Days Café",
            category=self.category,
            location=Point(ORIGIN_LNG, ORIGIN_LAT),
        )
        ratings = [5, 4, 3, 2]
        for i, rating in enumerate(ratings):
            user = User.objects.create_user(
                username=f"reviewer{i}", password="a-strong-password-123"
            )
            Review.objects.create(business=self.business, user=user, rating=rating)
        # expected average: (5+4+3+2)/4 = 3.5, count: 4

    def test_detail_endpoint_reports_correct_average_and_count(self):
        response = self.client.get(f"/api/businesses/{self.business.id}/")
        self.assertEqual(response.data["review_count"], 4)
        self.assertEqual(response.data["average_rating"], 3.5)

    def test_search_endpoint_reports_correct_average_and_count(self):
        response = self.client.get(
            f"/api/businesses/search?lat={ORIGIN_LAT}&lng={ORIGIN_LNG}"
        )
        result = response.data["results"][0]
        self.assertEqual(result["review_count"], 4)
        self.assertEqual(result["average_rating"], 3.5)

    def test_removed_reviews_excluded_from_average(self):
        # Remove the 2-star review — new average of [5,4,3] = 4.0, count 3
        Review.objects.filter(rating=2).update(is_removed=True)

        response = self.client.get(f"/api/businesses/{self.business.id}/")
        self.assertEqual(response.data["review_count"], 3)
        self.assertEqual(response.data["average_rating"], 4.0)

    def test_search_still_returns_one_row_per_business_not_one_per_review(self):
        """The most direct fan-out check: 4 reviews on 1 business must
        still produce exactly 1 search result, not 4 duplicate rows."""
        response = self.client.get(
            f"/api/businesses/search?lat={ORIGIN_LAT}&lng={ORIGIN_LNG}"
        )
        matching = [r for r in response.data["results"] if r["id"] == self.business.id]
        self.assertEqual(len(matching), 1)

    def test_business_with_no_reviews_reports_null_average_and_zero_count(self):
        empty_business = Business.objects.create(
            name="No Reviews Yet",
            category=self.category,
            location=Point(ORIGIN_LNG, ORIGIN_LAT),
        )
        response = self.client.get(f"/api/businesses/{empty_business.id}/")
        self.assertIsNone(response.data["average_rating"])
        self.assertEqual(response.data["review_count"], 0)

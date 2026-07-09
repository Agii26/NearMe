from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase

from categories.models import Category
from businesses.models import Business
from reviews.models import Review, ReviewFlag

User = get_user_model()


def _auth_header(client, username, password="a-strong-password-123"):
    login = client.post(
        "/api/auth/login/", {"username": username, "password": password}
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {login.data['access']}"}


class ReviewCreationTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.get(slug="food-dining")
        self.business = Business.objects.create(
            name="Better Days Café",
            category=self.category,
            location=Point(121.05, 14.65),
        )
        self.consumer = User.objects.create_user(
            username="maria", password="a-strong-password-123"
        )

    def test_requires_authentication(self):
        response = self.client.post(
            f"/api/businesses/{self.business.id}/reviews/",
            {"rating": 5, "text": "Great!"},
        )
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_leave_a_review(self):
        headers = _auth_header(self.client, "maria")
        response = self.client.post(
            f"/api/businesses/{self.business.id}/reviews/",
            {"rating": 5, "text": "Great!"},
            **headers,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Review.objects.filter(business=self.business, user=self.consumer).count(), 1
        )

    def test_rejects_rating_outside_1_to_5(self):
        headers = _auth_header(self.client, "maria")
        response = self.client.post(
            f"/api/businesses/{self.business.id}/reviews/", {"rating": 7}, **headers
        )
        self.assertEqual(response.status_code, 400)

    def test_cannot_review_the_same_business_twice(self):
        headers = _auth_header(self.client, "maria")
        self.client.post(
            f"/api/businesses/{self.business.id}/reviews/", {"rating": 4}, **headers
        )
        second = self.client.post(
            f"/api/businesses/{self.business.id}/reviews/", {"rating": 2}, **headers
        )
        self.assertEqual(second.status_code, 400)
        self.assertEqual(
            Review.objects.filter(business=self.business, user=self.consumer).count(), 1
        )

    def test_owner_cannot_review_their_own_business(self):
        owner = User.objects.create_user(
            username="owner", password="a-strong-password-123"
        )
        self.business.claimed = True
        self.business.owner = owner
        self.business.save()

        headers = _auth_header(self.client, "owner")
        response = self.client.post(
            f"/api/businesses/{self.business.id}/reviews/", {"rating": 5}, **headers
        )
        self.assertEqual(response.status_code, 400)

    def test_removed_reviews_do_not_appear_in_public_list(self):
        review = Review.objects.create(
            business=self.business, user=self.consumer, rating=1, text="bad"
        )
        review.is_removed = True
        review.save()

        response = self.client.get(f"/api/businesses/{self.business.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 0)

    def test_reviewer_can_delete_their_own_review(self):
        review = Review.objects.create(
            business=self.business, user=self.consumer, rating=3
        )
        headers = _auth_header(self.client, "maria")
        response = self.client.delete(f"/api/reviews/{review.id}/", **headers)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_user_cannot_delete_someone_elses_review(self):
        other = User.objects.create_user(
            username="juan", password="a-strong-password-123"
        )
        review = Review.objects.create(business=self.business, user=other, rating=3)
        headers = _auth_header(self.client, "maria")
        response = self.client.delete(f"/api/reviews/{review.id}/", **headers)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Review.objects.filter(id=review.id).exists())


class ReviewFlagTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.get(slug="food-dining")
        self.business = Business.objects.create(
            name="Better Days Café",
            category=self.category,
            location=Point(121.05, 14.65),
        )
        self.author = User.objects.create_user(
            username="author", password="a-strong-password-123"
        )
        self.reporter = User.objects.create_user(
            username="reporter", password="a-strong-password-123"
        )
        self.review = Review.objects.create(
            business=self.business, user=self.author, rating=1, text="spam"
        )

    def test_authenticated_user_can_flag_a_review(self):
        headers = _auth_header(self.client, "reporter")
        response = self.client.post(
            f"/api/reviews/{self.review.id}/flag/", {"reason": "spam"}, **headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ReviewFlag.objects.filter(review=self.review).count(), 1)

    def test_cannot_flag_the_same_review_twice(self):
        headers = _auth_header(self.client, "reporter")
        self.client.post(f"/api/reviews/{self.review.id}/flag/", {}, **headers)
        second = self.client.post(f"/api/reviews/{self.review.id}/flag/", {}, **headers)
        self.assertEqual(second.status_code, 400)

    def test_a_single_flag_does_not_hide_the_review(self):
        """A lone flag must not be enough to suppress a review — that would
        make it trivial to silence reviews someone simply dislikes."""
        headers = _auth_header(self.client, "reporter")
        self.client.post(f"/api/reviews/{self.review.id}/flag/", {}, **headers)

        response = self.client.get(f"/api/businesses/{self.business.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 1)

    def test_admin_removing_a_flagged_review_hides_it(self):
        ReviewFlag.objects.create(review=self.review, flagged_by=self.reporter)
        self.review.is_removed = True
        self.review.save()

        response = self.client.get(f"/api/businesses/{self.business.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 0)

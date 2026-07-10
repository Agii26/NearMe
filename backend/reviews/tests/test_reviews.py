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

    def test_new_review_defaults_to_visible(self):
        headers = _auth_header(self.client, "maria")
        self.client.post(
            f"/api/businesses/{self.business.id}/reviews/", {"rating": 5}, **headers
        )
        review = Review.objects.get(business=self.business, user=self.consumer)
        self.assertEqual(review.status, Review.VISIBLE)

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
        Review.objects.create(
            business=self.business,
            user=self.consumer,
            rating=1,
            text="bad",
            status=Review.REMOVED,
        )
        response = self.client.get(f"/api/businesses/{self.business.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 0)

    def test_hidden_pending_review_reviews_do_not_appear_in_public_list(self):
        Review.objects.create(
            business=self.business,
            user=self.consumer,
            rating=1,
            status=Review.HIDDEN_PENDING_REVIEW,
        )
        response = self.client.get(f"/api/businesses/{self.business.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 0)

    def test_reviewer_can_edit_their_own_review(self):
        review = Review.objects.create(
            business=self.business, user=self.consumer, rating=2, text="meh"
        )
        headers = _auth_header(self.client, "maria")
        response = self.client.patch(
            f"/api/reviews/{review.id}/",
            {"rating": 5, "text": "actually great"},
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "actually great")

    def test_user_cannot_edit_someone_elses_review(self):
        other = User.objects.create_user(
            username="juan", password="a-strong-password-123"
        )
        review = Review.objects.create(business=self.business, user=other, rating=3)
        headers = _auth_header(self.client, "maria")
        response = self.client.patch(
            f"/api/reviews/{review.id}/", {"rating": 1}, **headers
        )
        self.assertEqual(response.status_code, 403)

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
    """
    Per the Phase 3 roadmap spec: 'flagged reviews enter a moderation queue,
    hidden from public view until reviewed' — a single flag DOES hide the
    review immediately. This is a deliberate spec choice (not the more
    abuse-resistant 'needs multiple flags' alternative); see Review's
    docstring for the trade-off note.
    """

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

    def test_flagging_immediately_hides_the_review_from_public_view(self):
        headers = _auth_header(self.client, "reporter")
        self.client.post(f"/api/reviews/{self.review.id}/flag/", {}, **headers)

        self.review.refresh_from_db()
        self.assertEqual(self.review.status, Review.HIDDEN_PENDING_REVIEW)

        response = self.client.get(f"/api/businesses/{self.business.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 0)

    def test_unflagged_reviews_remain_visible(self):
        response = self.client.get(f"/api/businesses/{self.business.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 1)

    def test_admin_restore_makes_a_flagged_review_visible_again(self):
        ReviewFlag.objects.create(review=self.review, flagged_by=self.reporter)
        self.review.refresh_from_db()
        self.assertEqual(self.review.status, Review.HIDDEN_PENDING_REVIEW)

        self.review.restore()

        response = self.client.get(f"/api/businesses/{self.business.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 1)

    def test_admin_remove_keeps_a_flagged_review_hidden_permanently(self):
        ReviewFlag.objects.create(review=self.review, flagged_by=self.reporter)
        self.review.remove()

        self.review.refresh_from_db()
        self.assertEqual(self.review.status, Review.REMOVED)
        response = self.client.get(f"/api/businesses/{self.business.id}/reviews/")
        self.assertEqual(len(response.data["results"]), 0)

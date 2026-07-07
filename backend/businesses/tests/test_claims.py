from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase

from accounts.models import Profile
from categories.models import Category
from businesses.models import Business, BusinessClaim

User = get_user_model()


def _auth_header(client, username, password):
    login = client.post(
        "/api/auth/login/", {"username": username, "password": password}
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {login.data['access']}"}


class ClaimFlowTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.get(slug="food-dining")
        self.business = Business.objects.create(
            name="Better Days Café",
            category=self.category,
            location=Point(121.05, 14.65),
        )
        self.owner = User.objects.create_user(
            username="owner", password="a-strong-password-123"
        )
        self.owner.profile.role = Profile.BUSINESS_OWNER
        self.owner.profile.save()

    def test_claim_requires_authentication(self):
        response = self.client.post(f"/api/businesses/{self.business.id}/claim/")
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_submit_a_claim(self):
        headers = _auth_header(self.client, "owner", "a-strong-password-123")
        response = self.client.post(
            f"/api/businesses/{self.business.id}/claim/", **headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], BusinessClaim.PENDING)
        self.business.refresh_from_db()
        self.assertFalse(self.business.claimed)  # not claimed until approved

    def test_duplicate_pending_claim_is_rejected(self):
        headers = _auth_header(self.client, "owner", "a-strong-password-123")
        self.client.post(f"/api/businesses/{self.business.id}/claim/", **headers)
        second_attempt = self.client.post(
            f"/api/businesses/{self.business.id}/claim/", **headers
        )
        self.assertEqual(second_attempt.status_code, 400)

    def test_cannot_claim_an_already_claimed_business(self):
        other_owner = User.objects.create_user(
            username="already-owns", password="a-strong-password-123"
        )
        self.business.claimed = True
        self.business.owner = other_owner
        self.business.save()

        headers = _auth_header(self.client, "owner", "a-strong-password-123")
        response = self.client.post(
            f"/api/businesses/{self.business.id}/claim/", **headers
        )
        self.assertEqual(response.status_code, 400)

    def test_approving_a_claim_flips_claimed_and_sets_owner(self):
        claim = BusinessClaim.objects.create(business=self.business, user=self.owner)
        claim.approve()

        self.business.refresh_from_db()
        self.assertTrue(self.business.claimed)
        self.assertEqual(self.business.owner, self.owner)
        claim.refresh_from_db()
        self.assertEqual(claim.status, BusinessClaim.APPROVED)
        self.assertIsNotNone(claim.reviewed_at)

    def test_rejecting_a_claim_does_not_change_the_business(self):
        claim = BusinessClaim.objects.create(business=self.business, user=self.owner)
        claim.reject()

        self.business.refresh_from_db()
        self.assertFalse(self.business.claimed)
        self.assertEqual(claim.status, BusinessClaim.REJECTED)

    def test_my_claims_lists_only_the_requesting_users_claims(self):
        BusinessClaim.objects.create(business=self.business, user=self.owner)
        other_user = User.objects.create_user(
            username="someone-else", password="a-strong-password-123"
        )
        other_business = Business.objects.create(
            name="Other Biz", category=self.category, location=Point(121.0, 14.6)
        )
        BusinessClaim.objects.create(business=other_business, user=other_user)

        headers = _auth_header(self.client, "owner", "a-strong-password-123")
        response = self.client.get("/api/businesses/claims/mine/", **headers)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["business_name"], "Better Days Café"
        )


class OwnershipPermissionTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.get(slug="retail")
        self.owner = User.objects.create_user(
            username="rightful-owner", password="a-strong-password-123"
        )
        self.intruder = User.objects.create_user(
            username="intruder", password="a-strong-password-123"
        )
        self.business = Business.objects.create(
            name="IronWorks Hardware",
            category=self.category,
            location=Point(121.05, 14.65),
            claimed=True,
            owner=self.owner,
        )

    def test_anyone_can_read_a_business_profile(self):
        response = self.client.get(f"/api/businesses/{self.business.id}/")
        self.assertEqual(response.status_code, 200)

    def test_owner_can_edit_their_business(self):
        headers = _auth_header(self.client, "rightful-owner", "a-strong-password-123")
        response = self.client.patch(
            f"/api/businesses/{self.business.id}/",
            {"name": "IronWorks Hardware & Paint"},
            **headers,
        )
        self.assertEqual(response.status_code, 200)

    def test_non_owner_gets_403_when_editing(self):
        headers = _auth_header(self.client, "intruder", "a-strong-password-123")
        response = self.client.patch(
            f"/api/businesses/{self.business.id}/", {"name": "Hijacked Name"}, **headers
        )
        self.assertEqual(response.status_code, 403)
        self.business.refresh_from_db()
        self.assertEqual(self.business.name, "IronWorks Hardware")

    def test_anonymous_user_gets_401_when_editing(self):
        response = self.client.patch(
            f"/api/businesses/{self.business.id}/", {"name": "Anon Edit"}
        )
        self.assertEqual(response.status_code, 401)

    def test_dashboard_edit_is_immediately_reflected_in_public_listing(self):
        headers = _auth_header(self.client, "rightful-owner", "a-strong-password-123")
        self.client.patch(
            f"/api/businesses/{self.business.id}/",
            {"contact_phone": "0917 000 1111"},
            **headers,
        )
        public_view = self.client.get(f"/api/businesses/{self.business.id}/")
        self.assertEqual(public_view.data["contact_phone"], "0917 000 1111")

    def test_my_businesses_lists_only_owned_businesses(self):
        Business.objects.create(
            name="Not Mine",
            category=self.category,
            location=Point(121.0, 14.6),
            claimed=True,
            owner=self.intruder,
        )
        headers = _auth_header(self.client, "rightful-owner", "a-strong-password-123")
        response = self.client.get("/api/businesses/mine/", **headers)
        names = [b["name"] for b in response.data["results"]]
        self.assertEqual(names, ["IronWorks Hardware"])

import io

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from PIL import Image
from rest_framework.test import APITestCase

from categories.models import Category
from businesses.models import Business, Media

User = get_user_model()


def _tiny_png():
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), color="red").save(buffer, format="PNG")
    buffer.seek(0)
    buffer.name = "test.png"
    return buffer


def _auth_header(client, username, password):
    login = client.post(
        "/api/auth/login/", {"username": username, "password": password}
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {login.data['access']}"}


class PhotoUploadTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.get(slug="food-dining")
        self.owner = User.objects.create_user(
            username="owner", password="a-strong-password-123"
        )
        self.business = Business.objects.create(
            name="Better Days Café",
            category=self.category,
            location=Point(121.05, 14.65),
            claimed=True,
            owner=self.owner,
        )

    def test_owner_can_upload_a_photo(self):
        headers = _auth_header(self.client, "owner", "a-strong-password-123")
        response = self.client.post(
            f"/api/businesses/{self.business.id}/photos/",
            {"image": _tiny_png()},
            format="multipart",
            **headers,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Media.objects.filter(business=self.business).count(), 1)

    def test_non_owner_cannot_upload_a_photo(self):
        User.objects.create_user(username="intruder", password="a-strong-password-123")
        headers = _auth_header(self.client, "intruder", "a-strong-password-123")
        response = self.client.post(
            f"/api/businesses/{self.business.id}/photos/",
            {"image": _tiny_png()},
            format="multipart",
            **headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_uploaded_photo_appears_on_public_profile(self):
        headers = _auth_header(self.client, "owner", "a-strong-password-123")
        self.client.post(
            f"/api/businesses/{self.business.id}/photos/",
            {"image": _tiny_png()},
            format="multipart",
            **headers,
        )
        response = self.client.get(f"/api/businesses/{self.business.id}/")
        self.assertEqual(len(response.data["photos"]), 1)

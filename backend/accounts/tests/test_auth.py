from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from accounts.models import Profile

User = get_user_model()


class RegistrationTests(APITestCase):
    def test_register_creates_user_with_profile_and_role(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "juan_dela_cruz",
                "email": "juan@example.com",
                "password": "a-strong-password-123",
                "role": Profile.BUSINESS_OWNER,
            },
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username="juan_dela_cruz")
        self.assertEqual(user.profile.role, Profile.BUSINESS_OWNER)
        self.assertNotIn("password", response.data)

    def test_register_defaults_to_consumer_role(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "maria",
                "email": "maria@example.com",
                "password": "a-strong-password-123",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            User.objects.get(username="maria").profile.role, Profile.CONSUMER
        )

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="first", email="dupe@example.com", password="whatever-123"
        )
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "second",
                "email": "dupe@example.com",
                "password": "a-strong-password-123",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "weakpw", "email": "weak@example.com", "password": "12345"},
        )
        self.assertEqual(response.status_code, 400)


class LoginAndMeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="juan", email="juan@example.com", password="a-strong-password-123"
        )
        self.user.profile.role = Profile.BUSINESS_OWNER
        self.user.profile.save()

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "juan", "password": "a-strong-password-123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_wrong_password_is_rejected(self):
        response = self.client.post(
            "/api/auth/login/", {"username": "juan", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 401)

    def test_me_requires_authentication(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 401)

    def test_me_returns_authenticated_users_role(self):
        login = self.client.post(
            "/api/auth/login/",
            {"username": "juan", "password": "a-strong-password-123"},
        )
        access_token = login.data["access"]
        response = self.client.get(
            "/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "juan")
        self.assertEqual(response.data["profile"]["role"], Profile.BUSINESS_OWNER)

    def test_logout_blacklists_refresh_token(self):
        login = self.client.post(
            "/api/auth/login/",
            {"username": "juan", "password": "a-strong-password-123"},
        )
        access_token, refresh_token = login.data["access"], login.data["refresh"]

        logout = self.client.post(
            "/api/auth/logout/",
            {"refresh": refresh_token},
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(logout.status_code, 205)

        refresh_attempt = self.client.post(
            "/api/auth/refresh/", {"refresh": refresh_token}
        )
        self.assertEqual(refresh_attempt.status_code, 401)

# Tests for the accounts app — DRF API authentication endpoints.
# Guest login reads credentials from os.environ (not django.conf.settings).
import os
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class LoginAPITests(TestCase):
    """Tests for the POST /accounts/login/ endpoint."""

    def setUp(self):
        self.api_client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
        )

    def test_login_success(self):
        """Valid credentials should return 200 with JWT tokens."""
        response = self.api_client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_wrong_password(self):
        """Invalid password should return 400."""
        response = self.api_client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpassword',
        }, format='json')
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ])

    def test_login_nonexistent_user(self):
        """Login with a username that doesn't exist should fail."""
        response = self.api_client.post('/accounts/login/', {
            'username': 'nosuchuser',
            'password': 'anything',
        }, format='json')
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ])


class RegisterAPITests(TestCase):
    """Tests for the POST /accounts/register/ endpoint."""

    def setUp(self):
        self.api_client = APIClient()

    def test_register_success(self):
        """Valid registration data should create user and return tokens."""
        response = self.api_client.post('/accounts/register/', {
            'username': 'newuser',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        """Mismatched passwords should return 400."""
        response = self.api_client.post('/accounts/register/', {
            'username': 'newuser',
            'password': 'SecurePass123!',
            'password2': 'DifferentPass456!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Registering with an existing username should return 400."""
        User.objects.create_user(username='existing', password='pass123')
        response = self.api_client.post('/accounts/register/', {
            'username': 'existing',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GuestLoginTests(TestCase):
    """Tests for the POST /accounts/guest-login/ endpoint."""

    def setUp(self):
        self.api_client = APIClient()

    @patch.dict(os.environ, {'GUEST_USERNAME': 'mockguest', 'GUEST_PASSWORD': 'mockpassword'})
    def test_guest_login_success(self):
        """Guest login should return JWT tokens when credentials are valid."""
        # Create a user matching the mocked guest credentials
        User.objects.create_user(username='mockguest', password='mockpassword')
        response = self.api_client.post('/accounts/guest-login/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertEqual(response.data['user']['username'], 'mockguest')

    @patch.dict(os.environ, {'GUEST_USERNAME': 'mockguest', 'GUEST_PASSWORD': 'mockpassword'})
    def test_guest_login_failure_wrong_credentials(self):
        """Guest login should fail if the guest user doesn't exist in the DB."""
        # Don't create the guest user — credentials won't match anything
        response = self.api_client.post('/accounts/guest-login/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch.dict(os.environ, {}, clear=True)
    def test_guest_login_not_configured(self):
        """Guest login should return 503 when env vars are not set."""
        response = self.api_client.post('/accounts/guest-login/', format='json')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)


class LogoutAPITests(TestCase):
    """Tests for the POST /accounts/logout/ endpoint."""

    def setUp(self):
        self.api_client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
        )

    def test_logout_success(self):
        """Authenticated user can log out."""
        # Login first to get tokens
        login_response = self.api_client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        }, format='json')
        tokens = login_response.data['tokens']
        # Set auth header and logout
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = self.api_client.post('/accounts/logout/', {
            'refresh': tokens['refresh'],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        """Unauthenticated logout should return 401."""
        response = self.api_client.post('/accounts/logout/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
# Django base test case and settings access for temporary test overrides.
from django.test import TestCase
from django.conf import settings
# Project user model helper and patch utility for mocking settings values.
from django.contrib.auth import get_user_model
from unittest.mock import patch
# DRF API client is available for API-style tests where needed.
from rest_framework.test import APIClient

User = get_user_model()


class GuestLoginTests(TestCase):
    """Tests for guest authentication behavior using mocked guest settings."""

    def setUp(self):
        # Keep an API client ready for future API endpoint tests in this class.
        self.api_client = APIClient()

    @patch('django.conf.settings.GUEST_PASSWORD', 'mockpassword')
    @patch('django.conf.settings.GUEST_USERNAME', 'mockguest')
    def test_guest_login_view_success(self):
        """
        Test that a user can log in using the guest credentials,
        mocking the settings to ensure test isolation.
        This assumes a login URL at '/accounts/login/'.
        """
        # Read the mocked guest credentials from settings.
        guest_username = settings.GUEST_USERNAME
        guest_password = settings.GUEST_PASSWORD

        # Create a user matching those guest credentials.
        User.objects.create_user(
            username=guest_username,
            password=guest_password
        )

        # Submit the login form and follow redirects to the landing page.
        response = self.client.post('/accounts/login/', {
            'username': guest_username,
            'password': guest_password,
        }, follow=True)

        # Confirm login flow completes successfully.
        self.assertEqual(response.status_code, 200)
        # Check for a logout link, which usually appears after login.
        self.assertContains(response, 'Log out', msg_prefix="Logout link not found after login")
        # Verify the user is actually logged in and is the correct user.
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, guest_username)

    @patch('django.conf.settings.GUEST_PASSWORD', 'mockpassword')
    @patch('django.conf.settings.GUEST_USERNAME', 'mockguest')
    def test_guest_login_view_failure_wrong_password(self):
        """Test that a user cannot log in with an incorrect password."""
        # Read the mocked guest credentials from settings.
        guest_username = settings.GUEST_USERNAME
        guest_password = settings.GUEST_PASSWORD

        # Create a valid guest user first.
        User.objects.create_user(username=guest_username, password=guest_password)

        # Attempt login with an invalid password.
        response = self.client.post('/accounts/login/', {
            'username': guest_username,
            'password': 'wrongpassword',
        }, follow=True)

        # Response still returns 200 because form is re-rendered with errors.
        self.assertEqual(response.status_code, 200)
        # User should not be authenticated
        self.assertFalse(response.context['user'].is_authenticated)
        # Should probably see an error message on the login form.
        # This message is part of Django's default auth form.
        self.assertContains(response, "Please enter a correct username and password.")
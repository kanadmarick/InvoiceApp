# Smoke tests for core routes in the DRF-based API + Nginx-served SPA architecture.
# The React frontend is served by Nginx (not Django), so Django only serves:
#   - /admin/       → Django admin panel
#   - /api/docs/    → Swagger UI (drf-spectacular)
#   - /accounts/*   → DRF API endpoints (JSON)
#   - /businesses/* → DRF API endpoints (JSON)
#   - /billings/*   → DRF API endpoints (JSON)

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class PageAvailabilityTests(TestCase):
    """Basic smoke tests to verify key routes are reachable."""

    def setUp(self):
        self.api_client = APIClient()

    def test_admin_page(self):
        """Admin page should be reachable (redirects to login)."""
        response = self.client.get('/admin/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_swagger_ui(self):
        """Swagger API docs page should load successfully."""
        response = self.client.get('/api/docs/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_api_schema(self):
        """OpenAPI schema endpoint should return JSON."""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, 200)

    def test_404_page(self):
        """Requesting a non-existent URL should return 404."""
        response = self.client.get('/this-page-does-not-exist-at-all/')
        self.assertEqual(response.status_code, 404)

    def test_businesses_endpoint_requires_auth(self):
        """Businesses API should return 401 for unauthenticated requests."""
        response = self.api_client.get('/businesses/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invoices_endpoint_requires_auth(self):
        """Invoices API should return 401 for unauthenticated requests."""
        response = self.api_client.get('/billings/invoices/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_accounts_users_endpoint_requires_auth(self):
        """Accounts users API should deny unauthenticated access."""
        response = self.api_client.get('/accounts/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_endpoint_allows_unauthenticated(self):
        """Login API endpoint should accept unauthenticated POST requests."""
        response = self.api_client.post('/accounts/login/', {
            'username': 'nonexistent',
            'password': 'wrong',
        }, format='json')
        # Should return 400 (invalid credentials), not 403 or 405
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ])

    def test_register_endpoint_allows_unauthenticated(self):
        """Register API endpoint should accept unauthenticated POST requests."""
        response = self.api_client.post('/accounts/register/', {
            'username': 'newuser',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
        }, format='json')
        # Should return 201 (created) for valid data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

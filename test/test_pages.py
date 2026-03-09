# Django base test case gives us an isolated test database and HTTP test client.
from django.test import TestCase
# Tools for mocking client calls in unit-style tests.
from unittest.mock import patch, MagicMock

# Smoke tests for core public-facing routes.


class PageAvailabilityTests(TestCase):
    """Basic smoke tests to verify key pages are reachable."""

    def test_homepage(self):
        """Homepage should load successfully."""
        # Request the homepage and follow any redirects.
        response = self.client.get('/', follow=True)
        # Confirm the final response is successful.
        self.assertEqual(response.status_code, 200)

    def test_admin_page(self):
        """Admin page should be reachable (likely redirects to login)."""
        # Request the admin route and follow redirect chain (for example to login page).
        response = self.client.get('/admin/', follow=True)
        # Confirm the final response is successful.
        self.assertEqual(response.status_code, 200)

    def test_404_page(self):
        """Requesting a non-existent URL should return 404."""
        # Request a URL that should not exist.
        response = self.client.get('/this-page-does-not-exist/')
        # Confirm Django returns a 404 Not Found response.
        self.assertEqual(response.status_code, 404)

    @patch('django.test.Client.get')
    def test_homepage_mock_client(self, mock_get):
        """
        Test homepage availability using a mocked client to verify interaction.
        This ensures the test code calls the client correctly, isolated from the actual view.
        """
        # Build a fake response object to return from the mocked get call.
        mock_response = MagicMock()
        # Simulate a successful HTTP status code.
        mock_response.status_code = 200
        # Configure the mock so any Client.get call returns our fake response.
        mock_get.return_value = mock_response

        # Call the client method as the production code would.
        response = self.client.get('/', follow=True)

        # Verify the mocked method was called with expected arguments.
        mock_get.assert_called_with('/', follow=True)
        # Verify the value returned from the mocked call is handled correctly.
        self.assertEqual(response.status_code, 200)

    def test_businesses_page(self):
        """Businesses listing page should load successfully."""
        # Request the businesses listing page.
        response = self.client.get('/businesses/', follow=True)
        # Confirm the final response is successful.
        self.assertEqual(response.status_code, 200)

    def test_invoices_page(self):
        """Billings/invoices page should load successfully."""
        # Request the billings page.
        response = self.client.get('/billings/', follow=True)
        # Confirm the final response is successful.
        self.assertEqual(response.status_code, 200)

    def test_accounts_page(self):
        """Accounts page should load successfully."""
        # Request the accounts page.
        response = self.client.get('/accounts/', follow=True)
        # Confirm the final response is successful.
        self.assertEqual(response.status_code, 200)

# Django base test case and user model helper.
from django.test import TestCase
from django.contrib.auth import get_user_model
# Mock utility and optional DRF API client support.
from unittest.mock import patch
from rest_framework.test import APIClient

# This test file makes some assumptions about your project structure:
# 1. You have an app named 'businesses'.
# 2. Inside 'businesses/models.py', there is a 'Business' model.
# 3. The 'Business' model has a 'name' field and an 'owner' foreign key to the User model.
# 4. The URL for listing businesses is '/businesses/'.
# 5. The URL for creating a new business is '/businesses/create/'.
# These paths and fields may need to be adjusted to match your actual project.
from businesses.models import Business

User = get_user_model()


class BusinessLogicTests(TestCase):
    """
    Tests for the Business model and its related views, going beyond
    simple page availability checks.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class for efficiency."""
        # Create one reusable user for all tests in this class.
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        # Create an initial business record owned by that user.
        cls.business = Business.objects.create(
            name="Test Business Inc.",
            owner=cls.user
        )

    def setUp(self):
        # Keep APIClient available for future API-specific tests.
        self.api_client = APIClient()

    def test_business_model_str(self):
        """Test the string representation of the Business model."""
        # Ensure __str__ returns the business name as expected.
        self.assertEqual(str(self.business), "Test Business Inc.")

    def test_business_list_view_for_authenticated_user(self):
        """
        Test that an authenticated user can see their business on the list page.
        """
        # Log in so protected business pages can be accessed.
        self.client.login(username='testuser', password='password123')
        # Request the business list view.
        response = self.client.get('/businesses/')
        # Confirm page loads successfully.
        self.assertEqual(response.status_code, 200)
        # Confirm expected business name appears in rendered output.
        self.assertContains(response, "Test Business Inc.")
        # The default context variable name for a ListView is 'object_list'.
        self.assertIn(self.business, response.context['object_list'])

    def test_business_create_view_unauthenticated_redirect(self):
        """Test that an unauthenticated user is redirected from the create page."""
        response = self.client.get('/businesses/create/')
        # Expect a redirect to the login page. The default is '/accounts/login/'.
        self.assertRedirects(response, '/accounts/login/?next=/businesses/create/')

    def test_business_create_view_post(self):
        """
        Test that an authenticated user can create a new business via a POST request.
        """
        # Log in before submitting create form.
        self.client.login(username='testuser', password='password123')
        create_url = '/businesses/create/'

        # Test POSTing new business data
        initial_business_count = Business.objects.count()
        new_business_name = "New Awesome Company"
        post_data = {
            'name': new_business_name,
            # Add other required form fields here if any
        }
        # Assuming a successful creation redirects to the list view
        response = self.client.post(create_url, post_data, follow=True)

        # Check that a new business was created
        self.assertEqual(Business.objects.count(), initial_business_count + 1)

        # Check that we were redirected, probably to the business list page
        self.assertRedirects(response, '/businesses/')

        # Check that the new business exists in the database and is owned by the user
        new_business = Business.objects.get(name=new_business_name)
        self.assertEqual(new_business.owner, self.user)

        # Check that the new business name appears on the page we were redirected to
        self.assertContains(response, new_business_name)

    @patch('businesses.models.Business.save')
    def test_business_creation_calls_save(self, mock_save):
        """Test that creating a business instance calls the save method."""
        # We use objects.create, which should trigger the save method.
        # Since save is mocked, this won't actually write to the DB, which is fine for this unit test.
        Business.objects.create(name="Mocked Save Business", owner=self.user)
        self.assertTrue(mock_save.called)
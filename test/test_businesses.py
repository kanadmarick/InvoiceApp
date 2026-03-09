# Tests for the businesses app — DRF API endpoints.
# All business endpoints require JWT authentication.
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from businesses.models import Business

User = get_user_model()


class BusinessModelTests(TestCase):
    """Tests for the Business model."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123',
        )
        cls.business = Business.objects.create(
            name="Test Business Inc.",
            email="test@example.com",
            owner=cls.user,
        )

    def test_business_model_str(self):
        """Test the string representation of the Business model."""
        self.assertEqual(str(self.business), "Test Business Inc.")

    def test_business_owner_relationship(self):
        """Business should be linked to the correct owner."""
        self.assertEqual(self.business.owner, self.user)
        self.assertIn(self.business, self.user.businesses.all())


class BusinessAPITests(TestCase):
    """Tests for the Business DRF API endpoints."""

    def setUp(self):
        self.api_client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='password123',
        )
        self.business = Business.objects.create(
            name="Test Business Inc.",
            email="test@example.com",
            owner=self.user,
        )
        # Authenticate as testuser via JWT
        login_response = self.api_client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'password123',
        }, format='json')
        self.token = login_response.data['tokens']['access']
        self.api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_business_list_authenticated(self):
        """Authenticated user should see their own businesses."""
        response = self.api_client.get('/businesses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response is paginated — businesses are in 'results'
        results = response.data.get('results', response.data)
        business_names = [b['name'] for b in results]
        self.assertIn("Test Business Inc.", business_names)

    def test_business_list_unauthenticated(self):
        """Unauthenticated request should return 401."""
        client = APIClient()  # No credentials
        response = client.get('/businesses/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_create(self):
        """Authenticated user can create a new business via POST."""
        initial_count = Business.objects.count()
        response = self.api_client.post('/businesses/', {
            'name': 'New Awesome Company',
            'email': 'new@example.com',
            'address_line_1': '123 Main St',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Business.objects.count(), initial_count + 1)
        new_business = Business.objects.get(name='New Awesome Company')
        self.assertEqual(new_business.owner, self.user)

    def test_business_create_unauthenticated(self):
        """Unauthenticated user cannot create a business."""
        client = APIClient()
        response = client.post('/businesses/', {
            'name': 'Unauthorized Business',
            'email': 'unauth@example.com',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_detail(self):
        """Owner can retrieve their business details."""
        response = self.api_client.get(f'/businesses/{self.business.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Business Inc.")

    def test_business_update(self):
        """Owner can update their business via PATCH."""
        response = self.api_client.patch(f'/businesses/{self.business.id}/', {
            'name': 'Updated Business Name',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.business.refresh_from_db()
        self.assertEqual(self.business.name, 'Updated Business Name')

    def test_business_delete(self):
        """Owner can delete their business."""
        response = self.api_client.delete(f'/businesses/{self.business.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Business.objects.filter(id=self.business.id).exists())

    def test_business_isolation_between_users(self):
        """User should not see other users' businesses."""
        # Create a business owned by other_user
        Business.objects.create(
            name="Other User's Business",
            email="other@example.com",
            owner=self.other_user,
        )
        response = self.api_client.get('/businesses/')
        results = response.data.get('results', response.data)
        business_names = [b['name'] for b in results]
        self.assertNotIn("Other User's Business", business_names)
        self.assertIn("Test Business Inc.", business_names)
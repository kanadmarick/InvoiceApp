from django.test import TestCase


class PageAvailabilityTests(TestCase):
    def test_homepage(self):
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_businesses_page(self):
        response = self.client.get('/businesses/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_invoices_page(self):
        response = self.client.get('/billings/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_accounts_page(self):
        response = self.client.get('/accounts/', follow=True)
        self.assertEqual(response.status_code, 200)

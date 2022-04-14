from django.test import TestCase, RequestFactory, Client
from Contact import views


class ContactTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_ContactPage(self):
        request = self.factory.get('')
        response = views.contact_management(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)

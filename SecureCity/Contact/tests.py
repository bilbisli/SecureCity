from django.test import TestCase, RequestFactory, Client
from Contact import views
from django.test.utils import teardown_test_environment, setup_test_environment




class ContactTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_ContactPage(self):
        request = self.factory.get('')
        response = views.contact_management(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)

    def test_context(self):

        # GET response using the test client.
        response = self.client.get('/ContactManagement/')
        self.assertNotEqual(response.context['patrols'],None)
        self.assertNotEqual(response.context['contacts'],None)

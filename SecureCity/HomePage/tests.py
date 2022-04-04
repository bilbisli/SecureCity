from django.test import TestCase, RequestFactory
from HomePage import views

class AnimalTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_animals_can_speak(self):
        self.assertEqual('hello', 'hello')

    def test_homePage(self):
        request = self.factory.get('')
        response = views.home(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)

    def test_adminPage(self):
        request = self.factory.get('admin:index')
        response = views.home(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)



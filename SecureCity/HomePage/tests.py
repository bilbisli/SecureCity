from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase, RequestFactory, Client
from HomePage import views


class HomepageTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testerFinal2', 'tester@testing.com', 'testpassword')

    def test_animals_can_speak(self):
        self.assertEqual('hello', 'hello')

    def test_homePage(self):
        request = self.factory.get('')
        request.user = self.user
        response = views.home(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)

    def test_adminPage(self):
        request = self.factory.get('admin:index')
        request.user = self.user
        response = views.home(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)




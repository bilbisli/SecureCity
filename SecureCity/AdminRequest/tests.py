from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase, RequestFactory, Client
from AdminRequest import views


class AdminRequestTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testerFinal2', 'tester@testing.com', 'testpassword')


    def test_becomePatrolManager(self):
        request = self.factory.get('')
        request.user = self.user
        response = views.becomePatrolManager(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)

from django.test import TestCase

from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser, User
from datetime import datetime



from django.contrib.auth.models import User
import datetime
from Authentication.views import *
from Authentication.models import *
from Authentication.forms import *
from Patrols import models as PatrolModels

from Authentication.views import residentPage, AddParent, loginU


class SignUptest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_signupuser(self):
        request = self.factory.get('AddParent')
        response = AddParent(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)

    def test_login(self):
        request = self.factory.get('Login')
        response = loginU(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)


class Parenttest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testerFinal', 'tester@testing.com', 'testpassword')
        self.user.save()
        self.factory = RequestFactory()

    def test_signup_parent(self):
        request = self.factory.get('AddParent')
        request.user = AnonymousUser()
        response = AddParent(request)
        self.assertEqual(response.status_code, 200)

    def test_residentPage(self):
        logged_in = self.client.login(username='testerFinal', password='testpassword')
        self.assertTrue(logged_in)
        request = self.factory.get('resident_page')
        request.user = self.user
        response = residentPage(request)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.user.delete()


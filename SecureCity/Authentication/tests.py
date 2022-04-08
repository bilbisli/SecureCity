from django.test import TestCase

from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser, User
from datetime import datetime



from django.contrib.auth.models import User
import datetime
from Authentication.views import *
from Authentication.models import *
from Authentication.forms import *

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
        self.factory = RequestFactory()

    def test_signup_parent(self):
        request =  self.factory.get('AddParent')
        request.user = AnonymousUser()
        response = AddParent(request)
        self.assertEqual(response.status_code, 200)
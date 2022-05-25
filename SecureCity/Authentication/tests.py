from django.test import TestCase

from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser, User
from datetime import datetime

from django.contrib.auth.models import User
import datetime
from .views import *
from .models import *
from .forms import *

from django.test import tag
from adminPage.models import get_data


@tag('unitTest')
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


@tag('unitTest')
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

    def checkDb(self):
        df = get_data('unified_data')
        df = df.iloc[:, [2] + [i for i in range(49, 66)]]
        df = df.loc[df['neighborhood_1'] == self.user.profile.Neighborhood]
        df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x: int(x.replace(',', '')))
        #df.to_csv('officers1.csv', encoding="ISO-8859-8", index=False)
        self.assertTrue((df['neighborhood_1'] == self.user.profile.Neighborhood).all())
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


class PatrolManagementTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testerFinal', 'tester@testing.com', 'testpassword')
        self.user.save()
        self.factory = RequestFactory()
        self.client = Client()
        # assure login
        logged_in = self.client.login(username='testerFinal', password='testpassword')
        self.assertTrue(logged_in)

    def tearDown(self):
        user = User.objects.get(id=self.user.pk)
        self.client.logout()
        user.delete()

    def test_patrolManagement_not_manager(self):
        # test patrol management when user is not manager
        response = self.client.get('/PatrolManagement/')
        self.assertEqual(response.url, '/')
        # check that the user (which is not a manager) is redirected to the home page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertNotEqual(response.status_code, 404)

    def test_patrolManagement_is_manager(self):
        # self.client.logout()
        self.user.profile.is_patrol_manager = True
        self.user.profile.save()
        self.user.save()
        self.assertTrue(self.user.profile.is_patrol_manager)
        self.assertTrue(self.user.is_authenticated)
        # test patrol management when user is manager
        response = self.client.get('/PatrolManagement/')
        # check that the user (which is a manager) is arrives to the patrol management page
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)

    def test_patrolManagement_add_patrol(self):
        # self.client.logout()
        self.user.profile.is_patrol_manager = True
        self.user.profile.save()
        self.user.save()
        self.assertTrue(self.user.profile.is_patrol_manager)
        self.assertTrue(self.user.is_authenticated)
        # test adding a patrol
        response = self.client.post('/PatrolManagement/CreatePatrol')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)

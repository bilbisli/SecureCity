from django.http import HttpResponse, HttpResponseNotFound
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from django.urls import reverse, resolve

from Patrols.views import patrol_management, patrol_page

from Patrols.models import Patrol


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
        response = self.client.get(reverse('PatrolManagement'))
        # # check that the user (which is not a manager) is redirected to the home page
        self.assertEqual(response.url, reverse('homepage'))
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(response.status_code, 302)

    def test_patrolManagement_is_manager(self):
        # self.client.logout()
        self.user.profile.is_patrol_manager = True
        self.user.profile.save()
        self.user.save()
        self.assertTrue(self.user.profile.is_patrol_manager)
        self.assertTrue(self.user.is_authenticated)
        # test the url
        url = reverse('PatrolManagement')
        self.assertEqual(url, '/patrols/PatrolManagement/')
        # test patrol management when user is manager
        response = self.client.get(url, follow=True)
        resolver = resolve(url)
        # check that the user (which is a manager) arrives to the patrol management page
        self.assertNotEqual(response.status_code, 404)
        self.assertNotEqual(response.status_code, 302)
        self.assertEqual(response.status_code, 200)
        # check that the path to patrol management uses the correct view
        self.assertEqual(resolver.view_name, 'PatrolManagement')
        self.assertEqual(resolver.func, patrol_management)

    def test_patrolManagement_add_patrol(self):
        # self.client.logout()
        self.user.profile.is_patrol_manager = True
        self.user.profile.save()
        self.user.save()
        self.assertTrue(self.user.profile.is_patrol_manager)
        self.assertTrue(self.user.is_authenticated)
        # test adding a patrol
        response = self.client.post('/patrols/PatrolManagement/CreatePatrol')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 404)


class PatrolPageTest(TestCase):
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

    def test_patrol_page(self):
        # create a patrol
        patrol = Patrol.objects.create(title='testPatrol', description='testDescription', manager=self.user)
        # response = self.client.get('/patrols/PatrolManagement/PatrolPage/1')
        # test patrol page
        url = reverse('patrol_page', args=(patrol.pk,))
        self.assertEqual(url, f'/patrols/patrol/{patrol.pk}/')
        response = self.client.get(url, follow=True)
        resolver = resolve(url)
        # test url is of the post
        self.assertEqual(url, f'/patrols/patrol/{patrol.pk}/')
        # check that the user (which is a manager) arrives to the patrol management page
        self.assertNotEqual(response.status_code, 404)
        self.assertNotEqual(response.status_code, 302)
        self.assertEqual(response.status_code, 200)
        # check that the path to patrol management uses the correct view
        self.assertEqual(resolver.view_name, 'patrol_page')
        self.assertEqual(resolver.func, patrol_page)
        # test patrol page with wrong id
        non_existant_patrol_id = 999
        url = reverse('patrol_page', args=(non_existant_patrol_id,))
        self.assertEqual(url, f'/patrols/patrol/{non_existant_patrol_id}/')
        response = self.client.get(url, follow=True)
        resolver = resolve(url)
        # test that the path to patrol management uses the correct view
        self.assertEqual(resolver.view_name, 'patrol_page')
        # test that response leads to not found page
        self.assertEqual(response.__class__, HttpResponseNotFound)
        # test that response is not a redirect
        self.assertNotEqual(response.status_code, 302)
        # test that the response is not 200
        self.assertNotEqual(response.status_code, 200)
        # test that the response is 404
        self.assertEqual(response.status_code, 404)

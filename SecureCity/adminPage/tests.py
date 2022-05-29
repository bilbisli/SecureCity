from django.test import TestCase, RequestFactory, Client
from django.test import tag
from django.urls import reverse, resolve
from Patrols.models import Patrol
from django.contrib.auth.models import User
from adminPage.models import default_neighborhoods, get_locations, get_data, DataFile
from Authentication.views import residentPage
from adminPage.views import adminP, updateDatabases
from pandas import DataFrame


@tag('integrationTest')
class UpdateDBTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_superuser('testerFinal', 'tester@testing.com', 'testpassword')
        self.user.profile.is_patrol_manager = True
        self.user.profile.Neighborhood = 'ו'
        self.user.save()
        logged_in = self.client.login(username='testerFinal', password='testpassword')
        self.assertTrue(logged_in)
        self.no_data_msg = 'No data found.'
        self.success_data_update_msg = "Successfully updated databases"
        self.non_default_area = 'ו'
        self.default_area = 'ד'
        self.data_display_page = 'resident_page'
        self.admin_page = 'adminPage'
        self.update_db_view = 'updateDatabases'

    def tearDown(self):
        self.user.delete()
        self.client.logout()
        self.assertFalse(self.client.login(username='testerFinal', password='testpassword'))

    def Test_data_fetch_fail(self):
        """
        This test is to check if when trying to fetch the data from the db before api db update - the data is not
        fetching fails (None is returned as no data is present in db)
        """
        data = get_data()
        self.assertIsNone(data)

    def Test_locations_b4_db_update(self):
        """
        This test is to check if the locations are the default before the database is updated
        """
        locations = tuple(location[0] for location in get_locations())
        self.assertEqual(locations, default_neighborhoods)
        self.assertIn(self.default_area, locations)
        self.assertNotIn(self.non_default_area, locations)

    def Test_my_page_patrol_manager_no_data(self):
        """
        This test is to check if the myPage for patrol managers works correctly when no data is present in db
        """
        url = reverse(self.data_display_page)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        resolver = resolve(url)
        self.assertEqual(resolver.view_name, self.data_display_page)
        self.assertEqual(resolver.func, residentPage)
        self.assertTemplateUsed(response, 'Authentication/residentPage.html')
        self.assertContains(response, self.no_data_msg)
        self.assertNotContains(response, f'<th>{self.non_default_area}</th>')

    def Test_api_db_update_from_view(self):
        """
        This test is to check if the view for updating the database is works correctly
        """
        url = reverse(self.update_db_view)
        resolver = resolve(url)
        self.assertEqual(resolver.view_name, self.update_db_view)
        self.assertEqual(resolver.func, updateDatabases)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.success_data_update_msg)

    def Test_data_fetch_success(self):
        """
        This test is to check if the data is fetched after the database is updated
        """
        data = get_data()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, DataFrame)

    def Test_locations_after_db_update(self):
        """
        This test is to check if the locations are updated after the database is updated
        """
        locations = tuple(location[0] for location in get_locations())
        self.assertNotEqual(locations, default_neighborhoods)
        self.assertIn(self.default_area, locations)
        self.assertIn(self.non_default_area, locations)

    def Test_my_page_patrol_manager_with_data(self):
        """
        This test is to check if the myPage for patrol managers works correctly when no data is present in db
        """
        response = self.client.get(reverse(self.data_display_page), follow=True)
        self.assertTemplateUsed(response, 'Authentication/residentPage.html')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.no_data_msg)
        self.assertContains(response, f'<th>{self.non_default_area}</th>')

    @tag('integrationTest')
    def test_db_update_sequence(self):
        self.Test_data_fetch_fail()
        self.Test_locations_b4_db_update()
        self.Test_my_page_patrol_manager_no_data()
        self.Test_api_db_update_from_view()
        self.Test_data_fetch_success()
        self.Test_locations_after_db_update()
        self.Test_my_page_patrol_manager_with_data()

import time
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from HomePage import views
from django.test import tag
from adminPage.models import update_data
from adminPage.views import demographic_tables_build
from adminPage.views import crime_df_clean


@tag('unitTest')
class HomepageTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testerFinal2', 'tester@testing.com', 'testpassword')

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


@tag('measureApiResponse')
class MeasureApiResponseTestCase(TestCase):
    """
    Test the response of the API
    """
    def setUp(self):
        # start timer
        self.start_time = time.time()

    def test_measure_stat_area_response(self):
        tick = time.time() - self.start_time
        # Update the stat-area database
        statistical_areas_df = update_data(data_name='stat_n-hoods_table',
                                           api_endpoint='https://opendataprod.br7.org.il/api/3/',
                                           data_packages_search_path='action/package_search?q=',
                                           data_search_path='action/datastore_search?resource_id=',
                                           )
        toc = time.time()
        print('statistical areas db updated in: ', tick - toc)

    def test_measure_demographics_response(self):
        tick = time.time() - self.start_time
        # Update the demographic database
        unified_demographics = update_data(data_name='demographics',
                                           api_endpoint='https://opendataprod.br7.org.il/api/3/',
                                           data_packages_search_path='action/package_search?q=',
                                           data_search_path='action/datastore_search?resource_id=',
                                           df_preprocessing_function=demographic_tables_build,
                                           to_df=False,
                                           save=False,
                                           )
        toc = time.time()
        print('demographics db updated in: ', tick - toc)

    def test_measure_crime_rates_response(self):
        tick = time.time() - self.start_time
        # Update the crime database
        crime_rates_df = update_data(data_name='crime_records_data',
                                     api_endpoint='https://data.gov.il/api/3/',
                                     data_packages_search_path='action/package_search?q=',
                                     data_search_path='action/datastore_search?resource_id=',
                                     df_preprocessing_function=crime_df_clean,
                                     )
        toc = time.time()
        print('crime db updated in: ', tick - toc)

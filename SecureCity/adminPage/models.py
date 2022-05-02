from django.db import models
import pandas as pd
import requests
from django.db.models import JSONField


class DataFile(models.Model):
    """
    Model for the api data files
    """
    data = JSONField("data")
    file_name = models.CharField(max_length=255)
    is_backup = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)

    @classmethod
    def put_frame(cls, data_frame, file_name, is_backup=False, is_primary=False):
        stored_data_frame = cls(data=data_frame.to_json(orient='split'), file_name=file_name, is_backup=is_backup,
                                is_primary=is_primary)
        stored_data_frame.save()
        return stored_data_frame

    def load_frame(self):
        return pd.read_json(self.data, orient='split')

    def __str__(self):
        return f'{self.file_name}{f" (backup)" if self.is_backup else ""}{f" (primary)" if self.is_primary else ""}'


def update_data(api_endpoint='https://data.gov.il/api/3',
                api_url='action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e',
                data='crime',
                limit=10 ** 9):
    # handle past data
    current_data = DataFile.objects.filter(file_name=data)
    print('here')
    for data_file in current_data:
        print('there')
        if data_file.is_primary:
            print('detect')
            data_file.is_primary = False
            data_file.save()
        else:
            print('delete')
            data_file.delete()

    # get the data from the api
    url = f'{api_endpoint}/{api_url}&limit={limit}'
    response = requests.get(url)
    crime_rates_db = response.json()['result']['records']
    crime_rates_df = pd.DataFrame(crime_rates_db)
    # city_query = 'באר שבע'    # filter by city
    # crime_rates_df = crime_rates_df[crime_rates_df['Settlement_Council'] == city_query]       # filter by city
    crime_rates_df = crime_rates_df[
        crime_rates_df['StatArea'].notna() & crime_rates_df['StatisticCrimeGroup'].notna()]
    crime_rates_df['StatArea'] = [int(stat_number) % 1000 for stat_number in crime_rates_df['StatArea']]

    return DataFile.put_frame(data_frame=crime_rates_df, file_name=data, is_primary=True)


# get the current  data
def get_data(data='crime'):
    current_data = DataFile.objects.filter(file_name=data, is_primary=True)
    return current_data.first().load_frame()

from django.db import models
import pandas as pd
import requests
from django.db.models import JSONField
from django.utils import timezone


def current_time():
    return timezone.localtime(timezone.now())


class DataFile(models.Model):
    """
    Model for the api data files
    """
    data = JSONField("data")
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=current_time, blank=True, null=True)
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
        return f'{self.file_name}{f" (backup)" if self.is_backup else ""}{f" (primary)" if self.is_primary else ""}' \
               f'{" | added at: " + str(self.created_at) if self.created_at else ""}'


def organize_primary_and_backup_data(data_name):
    current_data = DataFile.objects.filter(file_name=data_name)
    for data_file in current_data:
        if data_file.is_primary:
            data_file.is_primary = False
            data_file.is_backup = True
            data_file.save()
        else:
            data_file.delete()


def update_data(data_name='crime_records_data',
                api_endpoint='https://data.gov.il/api/3/',
                # api_url='action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e')
                data_packages_search_path='/action/package_search?q=',
                data_search_path='action/datastore_search?resource_id=',
                limit=10 ** 9,
                df_preprocessing_function=None,
                organize_func=organize_primary_and_backup_data,
                to_df=True,
                save=True,):
    # get the data from the api
    package_search_url = f'{api_endpoint}{data_packages_search_path}{data_name}'
    results = requests.get(package_search_url).json()['result']['results'][0]['resources']
    db = filter(lambda r: r['format'] in ['exel', 'JSON', 'XLSX', 'CSV', 'EXCEL'], results)

    if to_df:
        db = next(db)
        try:
            db_id = db['id']
            db_url = f'{api_endpoint}{data_search_path}{db_id}&limit={limit}'
            response = requests.get(db_url)
            db = response.json()['result']['records']
            db = pd.DataFrame.from_records(db)
        except KeyError:
            db_url = db['url']
            db = pd.read_excel(db_url)

    df = db

    if df_preprocessing_function:
        df = df_preprocessing_function(df)

    print(f'{data_name}\ncolumn list: {df}')

    if not save:
        return df

    # handle past data
    if organize_func is not None:
        organize_func(data_name)

    return DataFile.put_frame(data_frame=df, file_name=data_name, is_primary=True)


# get the current  data
def get_data(data='unified_data'):
    current_data = DataFile.objects.filter(file_name=data, is_primary=True)
    if current_data.count() == 0:
        current_data = DataFile.objects.filter(file_name=data)
    return current_data.first().load_frame()



from django.db import models
import pandas as pd
import requests
from django.db.models import JSONField
from django.utils import timezone


default_neighborhoods = ('א', 'ב', 'ג', 'ד', 'ה')


def current_time():
    return timezone.localtime(timezone.now())


def get_locations(neighborhood_table='unified_data', neighborhood_column='neighborhood_1'):
    try:
        neighbourhoods = get_data(neighborhood_table)[neighborhood_column].unique()
    except (ValueError, KeyError, TypeError, AttributeError):
        neighbourhoods = default_neighborhoods

    return [(neighborhood, neighborhood) for neighborhood in neighbourhoods]


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
                save=True, ):
    # get the data from the API
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

    if not save:
        return df

    # handle past data
    if organize_func is not None:
        organize_func(data_name)

    # save the data
    ret = DataFile.put_frame(data_frame=df, file_name=data_name, is_primary=True)
    if to_df:
        ret = ret.load_frame()
    return ret


# get the current  data
def get_data(data='unified_data'):
    current_data = DataFile.objects.filter(file_name=data, is_primary=True)
    if current_data.count() == 0:
        current_data = DataFile.objects.filter(file_name=data)
    try:
        return current_data.first().load_frame()
    except AttributeError:
        return None


def unify_data(*data_frames, on_column):
    unified_data = data_frames[0]
    for df in data_frames:
        unified_data = pd.merge(unified_data, df, on=on_column, suffixes=('', '_y'))
        unified_data.drop(unified_data.filter(regex='_y$').columns.tolist(), axis=1, inplace=True)
    return unified_data


def crime_df_clean(df, city_query='באר שבע'):
    df = df[df['Settlement_Council'] == city_query]
    df = df[df['StatArea'].notna() & df['StatisticCrimeGroup'].notna()]
    df['StatArea'] = [int(stat_number) % 1000 for stat_number in df['StatArea']]
    crime_rates_df = pd.DataFrame()
    for stat_area in df['StatArea'].unique():
        temp_d = {"אג''ס": stat_area}
        for crime_category in df['StatisticCrimeGroup'].unique():
            count_pairs = len(df[(df['StatisticCrimeGroup'] == crime_category) & (
                    df['StatArea'] == stat_area)])
            temp_d[crime_category] = count_pairs
        crime_rates_df = pd.concat([crime_rates_df, pd.DataFrame.from_records([temp_d])], ignore_index=True)

    for crime_category in crime_rates_df:
        crime_rates_df[crime_category] = crime_rates_df[crime_category].astype(int)
    crime_rates_df["אג''ס"] = crime_rates_df["אג''ס"].astype(int)

    return crime_rates_df


def demographic_tables_build(df, stat_area_column="אג''ס"):
    unified_demographics = pd.read_csv('static/lamas_simplified.csv')
    unified_demographics = unified_demographics.drop(columns=unified_demographics.columns[-1:]).drop(
        columns=unified_demographics.columns[0])

    for table in filter(lambda r: r['format'] == 'JSON', df):
        # table_name = 'דמוגרפיה-' + table['name'].replace(' - JSON', "")
        temp_table = pd.DataFrame.from_records(requests.get(table['url']).json())
        unified_demographics = unify_data(unified_demographics, temp_table, on_column=stat_area_column)

    unified_demographics[stat_area_column] = unified_demographics[stat_area_column].astype(int)
    # unified_demographics.set_index(stat_area_column, inplace=True)

    data_name = 'unified_demographics'
    organize_primary_and_backup_data(data_name)
    DataFile.put_frame(data_frame=unified_demographics, file_name=data_name, is_primary=True)

    return unified_demographics


def updateData():
    heb_stat_area_column = "אג''ס"
    stat_area_column = 'stat-area'
    # Update the stat-area database
    statistical_areas_df = update_data(data_name='stat_n-hoods_table',
                                       api_endpoint='https://opendataprod.br7.org.il/api/3/',
                                       # api_url='action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e')
                                       data_packages_search_path='action/package_search?q=',
                                       data_search_path='action/datastore_search?resource_id=',
                                       )
    # Update the demographic database
    unified_demographics = update_data(data_name='demographics',
                                       api_endpoint='https://opendataprod.br7.org.il/api/3/',
                                       # api_url='action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e')
                                       data_packages_search_path='action/package_search?q=',
                                       data_search_path='action/datastore_search?resource_id=',
                                       df_preprocessing_function=demographic_tables_build,
                                       to_df=False,
                                       save=False,
                                       )

    # Update the crime database
    crime_rates_df = update_data(data_name='crime_records_data',
                                 api_endpoint='https://data.gov.il/api/3/',
                                 # api_url='action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e')
                                 data_packages_search_path='action/package_search?q=',
                                 data_search_path='action/datastore_search?resource_id=',
                                 df_preprocessing_function=crime_df_clean,
                                 )

    lamas_demographics = pd.read_csv('static/lamas_simplified.csv')
    lamas_demographics = lamas_demographics.iloc[2:, :-1]
    lamas_demographics[heb_stat_area_column] = lamas_demographics[heb_stat_area_column].astype(int)
    statistical_areas_df[heb_stat_area_column] = statistical_areas_df[stat_area_column].astype(int)
    statistical_areas_df.drop(stat_area_column, axis=1, inplace=True)
    unified_data = unify_data(lamas_demographics, unified_demographics, crime_rates_df, statistical_areas_df,
                              on_column=heb_stat_area_column)
    organize_primary_and_backup_data('unified_data')
    DataFile.put_frame(data_frame=unified_data, file_name='unified_data', is_primary=True)



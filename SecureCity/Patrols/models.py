from math import ceil

import pandas as pd
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from django.urls import reverse
from django.db.models import signals
from django.dispatch import dispatcher, receiver
from adminPage.models import get_data, get_locations

# string lengths

MIN_STRING = 15
SMALL_STRING = 31
MEDIUM_STRING = 63
LARGE_STRING = 255
XL_STRING = 511
MAX_STRING = 1023


def current_time():
    return timezone.localtime(timezone.now())


def get_priority(area):
    return get_priorities()[area]


def get_priorities():
    areas_df = analyze_patrols_priority()
    priorities_dict = pd.Series(areas_df['priority'].values, index=areas_df['stat-area']).to_dict()
    return priorities_dict


def get_patrol_size(area):
    return get_amount_of_people()[area]


def get_amount_of_people():
    try:
        areas_df = analyze_patrols_priority()
        amount_of_people_dict = pd.Series(areas_df['amount_of_people'].values, index=areas_df['stat-area']).to_dict()
    except (ValueError, KeyError, TypeError, AttributeError):
        amount_of_people_dict = {neighborhood: priority + 1 for priority, neighborhood in
                                 enumerate(['שכונה א', 'שכונה ב', 'שכונה ג', 'שכונה ד', 'שכונה ה'])}

    return amount_of_people_dict


class Patrol(models.Model):
    class PatrolStatus(models.TextChoices):
        CREATION = "Creation"
        ACTIVE = "Active"
        ARCHIVE = "Archive"

    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patrols', null=False)
    title = models.CharField('title', max_length=MEDIUM_STRING)
    patrol_status = models.CharField('patrol status', max_length=MIN_STRING, null=True, choices=PatrolStatus.choices,
                                     default=PatrolStatus.CREATION)
    description = models.TextField('description', max_length=MAX_STRING, null=True, blank=True)
    time_created = models.DateTimeField('time created', default=current_time, null=False)
    time_updated_last = models.DateTimeField('last updated', default=current_time, null=False)
    location = models.CharField(max_length=MEDIUM_STRING, choices=get_locations())
    date = models.DateField('date', default=current_time, null=False)
    start_time = models.TimeField('start time', default=current_time, null=False)
    end_time = models.TimeField('end time', default=current_time() + timezone.timedelta(hours=3), null=False)
    # TODO update automatic priority based on api in 'get_priority' function
    priority = models.IntegerField('priority', default=5)
    # TODO update automatic priority based on api in 'get_patrol_size' function
    participants_needed = models.IntegerField('participants needed', default=2)
    reactions = models.ManyToManyField(User, related_name='reactions', blank=True)
    approved_reactions = models.ManyToManyField(User, related_name='approved_reactions', blank=True)
    users_participated = models.ManyToManyField(User, related_name='participants', blank=True)

    def __str__(self):
        return f'title: {self.title} | location: {self.location} | priority: {self.priority} | ' \
               f'manager: {self.manager} | date: {self.date} | between: {self.start_time}-{self.end_time}'

    def get_fields_values(self):
        return [(field.name, field.value_to_string(self)) for field in Patrol._meta.fields]

    def get_absolute_url(self):
        return reverse('patrol', args=(str(self.pk),))

    def save(self, *args, **kwargs):
        self.priority = get_priority(self.location)
        super(Patrol, self).save(*args, **kwargs)  # Call the "real" save() method.


def analyze_patrols_priority(parameters=(
        'עבירות כלפי המוסר', 'עבירות כלפי הרכוש', 'עבירות נגד גוף', 'עבירות סדר ציבורי', 'עבירות מין',
        'עבירות נגד אדם',)):
    data_df = get_data()
    neighborhood_table = 'stat_n-hoods_table'
    neighborhood_column = 'neighborhood_1'
    stat_area_column = 'stat-area'
    heb_stat_area_column = "אג''ס"
    total_offenses_column = 'total_offenses'
    heb_total_residents_column = "סה''כ"
    total_residents_column = 'total_residents'
    ratio_column = 'residents_offense_ratio'
    areas_df = get_data(neighborhood_table)

    # take care of the case where there is no data in the database
    if areas_df is None or data_df is None:
        return None

    neighbourhoods = areas_df[neighborhood_column].unique()

    data_df[total_offenses_column] = data_df[list(parameters)].sum(axis=1)
    # data_df.to_excel('static/offenses.xlsx', index=False)

    # locations = [location[0] for location in get_locations()]
    data_df[stat_area_column] = data_df[heb_stat_area_column]
    data_df[total_residents_column] = data_df[heb_total_residents_column]
    #      סה''כ
    unified_data = unify_data(areas_df[[neighborhood_column, stat_area_column]],
                              data_df[[stat_area_column, total_offenses_column, total_residents_column]],
                              on_column=stat_area_column)

    neighborhoods_df = unified_data.groupby(neighborhood_column).sum()
    neighborhoods_df[ratio_column] = neighborhoods_df[total_residents_column] / neighborhoods_df[
        total_offenses_column]

    max_ratio = neighborhoods_df[ratio_column].max()
    min_ratio = neighborhoods_df[ratio_column].min()
    neighborhoods_df['priority'] = neighborhoods_df[ratio_column].apply(
        lambda x: max(1, round(((x - min_ratio) / (max_ratio - min_ratio)) * 5)))

    max_population = neighborhoods_df[total_residents_column].max()
    min_population = neighborhoods_df[total_residents_column].min()

    neighborhoods_df['people_needed'] = neighborhoods_df[total_residents_column].apply(
        lambda x: max(2, round(((x - min_population) / (max_population - min_population)) * 10)))

    return neighborhoods_df


def unify_data(*data_frames, on_column):
    unified_data = data_frames[0]
    for df in data_frames:
        unified_data = pd.merge(unified_data, df, on=on_column, suffixes=('', '_y'))
        unified_data.drop(unified_data.filter(regex='_y$').columns.tolist(), axis=1, inplace=True)
    return unified_data


from math import ceil

import pandas as pd
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from django.urls import reverse
from django.db.models import signals
from django.dispatch import dispatcher, receiver
from adminPage.models import get_data, get_locations, default_neighborhoods
from Authentication.views import crime_columns


# string lengths
MIN_STRING = 15
SMALL_STRING = 31
MEDIUM_STRING = 63
LARGE_STRING = 255
XL_STRING = 511
MAX_STRING = 1023
MIN_PARTICIPANTS = 2
DEFAULT_PATROL_SIZE = MIN_PARTICIPANTS
MAX_PRIORITY = 5
MAX_PARTICIPANTS = 10


def current_time():
    return timezone.localtime(timezone.now())


def get_priority(area):
    return get_priorities()[area]


def get_priorities():
    try:
        neighborbood_column = "neighborhood_1"
        areas_df = analyze_patrols_priority()
        print('areas df:')
        print(areas_df)
        priorities_dict = pd.Series(areas_df['priority'].values, index=areas_df[neighborbood_column]).to_dict()

    except (ValueError, KeyError, TypeError, AttributeError) as e:
        priorities_dict = {neighborhood: DEFAULT_PATROL_SIZE for priority, neighborhood in
                           enumerate(default_neighborhoods)}
    print(priorities_dict)
    return priorities_dict


def get_patrol_size(area):
    patrol_size = get_amount_of_people()
    if area not in patrol_size:
        return DEFAULT_PATROL_SIZE
    return patrol_size[area]


def get_amount_of_people():
    try:
        areas_df = analyze_patrols_priority()
        amount_of_people_dict = pd.Series(areas_df['people_needed'].values, index=areas_df.index).to_dict()
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        amount_of_people_dict = {neighborhood: priority + 1 for priority, neighborhood in
                                 enumerate(default_neighborhoods)}
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
    description = models.TextField('summary', max_length=MAX_STRING, null=True, blank=True)
    time_created = models.DateTimeField('time created', default=current_time, null=False)
    time_updated_last = models.DateTimeField('last updated', default=current_time, null=False)
    location = models.CharField(max_length=MEDIUM_STRING, choices=get_locations(), default=default_neighborhoods[0])
    date = models.DateField('date', default=current_time, null=False)
    start_time = models.TimeField('start time', default=current_time, null=False)
    end_time = models.TimeField('end time', default=current_time() + timezone.timedelta(hours=3), null=False)
    priority = models.IntegerField('priority', default=MAX_PRIORITY, blank=True)
    participants_needed = models.IntegerField('participants needed', default=DEFAULT_PATROL_SIZE)
    reactions = models.ManyToManyField(User, related_name='reactions', blank=True)
    approved_reactions = models.ManyToManyField(User, related_name='approved_reactions', blank=True)
    users_participated = models.ManyToManyField(User, related_name='participants', blank=True)
    update_priority = models.BooleanField(default=False)

    def __str__(self):
        return f'title: {self.title} | location: {self.location} | priority: {self.priority} | ' \
               f'manager: {self.manager} | date: {self.date} | between: {self.start_time}-{self.end_time}'

    def get_fields_values(self):
        return [(field.name, field.value_to_string(self)) for field in Patrol._meta.fields]

    def get_absolute_url(self):
        return reverse('patrol', args=(str(self.pk),))

    def save(self, *args, **kwargs):
        if not self.update_priority:
            self.priority = get_priority(self.location)
        else:
            self.update_priority = False
        super(Patrol, self).save(*args, **kwargs)  # Call the "real" save() method.


def analyze_patrols_priority(parameters=crime_columns):
    unified_data = get_data('unified_data')
    neighborhood_column = 'neighborhood_1'
    stat_area_column = "אג''ס"
    total_offenses_column = 'total_offenses'
    total_residents_column = "סה''כ"
    ratio_column = 'residents_offense_ratio'

    # take care of the case where there is no data in the database
    if unified_data is None:
        return None

    unified_data[total_offenses_column] = unified_data[list(parameters)].sum(axis=1)

    unified_data = unified_data[[neighborhood_column, stat_area_column, total_offenses_column, total_residents_column]]
    neighborhoods_df = unified_data.groupby(neighborhood_column).sum()
    neighborhoods_df[ratio_column] = neighborhoods_df[total_residents_column] / neighborhoods_df[total_offenses_column]

    max_ratio = neighborhoods_df[ratio_column].max()
    min_ratio = neighborhoods_df[ratio_column].min()
    neighborhoods_df['priority'] = neighborhoods_df[ratio_column].apply(
        lambda x: max(1, round(((x - min_ratio) / (max_ratio - min_ratio)) * MAX_PRIORITY)))

    max_population = neighborhoods_df[total_residents_column].max()
    min_population = neighborhoods_df[total_residents_column].min()

    neighborhoods_df['people_needed'] = neighborhoods_df[total_residents_column].apply(
        lambda x: max(2, round(((x - min_population) / (max_population - min_population)) * MAX_PARTICIPANTS)))

    return neighborhoods_df

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from django.urls import reverse
from django.db.models import signals
from django.dispatch import dispatcher, receiver
from adminPage.models import get_data

# string lengths
MIN_STRING = 15
SMALL_STRING = 31
MEDIUM_STRING = 63
LARGE_STRING = 255
XL_STRING = 511
MAX_STRING = 1023


def current_time():
    return timezone.localtime(timezone.now())


# TODO: after api connection is made, add location options
def get_locations():
    return [('A', 'שכונה א'), ('B', 'שכונה ב'), ('C', 'שכונה ג'), ('D', 'שכונה ד')]


# TODO: after api connection is made, add automatic priority calculation
def get_priority():
    return 1


# TODO: after api connection is made, add automatic patrol size calculation
def get_patrol_size():
    return 3


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
    # TODO: update location options based on api in 'get_locations' function
    location = models.CharField(max_length=MEDIUM_STRING, choices=get_locations())
    date = models.DateField('date', default=current_time, null=False)
    start_time = models.TimeField('start time', default=current_time, null=False)
    end_time = models.TimeField('end time', default=current_time() + timezone.timedelta(hours=3), null=False)
    # TODO update automatic priority based on api in 'get_priority' function
    priority = models.IntegerField('priority', default=get_priority())
    # TODO update automatic priority based on api in 'get_patrol_size' function
    participants_needed = models.IntegerField('participants needed', default=get_patrol_size())
    reactions = models.ManyToManyField(User, related_name='reactions', blank=True)
    approved_reactions = models.ManyToManyField(User, related_name='approved_reactions', blank=True)
    users_participated = models.ManyToManyField(User, related_name='participants', blank=True)

    def get_fields_values(self):
        return [(field.name, field.value_to_string(self)) for field in Patrol._meta.fields]

    def __str__(self):
        return f'title: {self.title} | location: {self.location} | priority: {self.priority} | ' \
               f'manager: {self.manager} | date: {self.date} | between: {self.start_time}-{self.end_time}'

    def get_absolute_url(self):
        return reverse('patrol', args=(str(self.pk),))


from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.urls import reverse

# string lengths
MIN_STRING = 15
SMALL_STRING = 31
MEDIUM_STRING = 63
LARGE_STRING = 255
XL_STRING = 511
MAX_STRING = 1023


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

    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patrols', null=True)
    title = models.CharField('title', max_length=MEDIUM_STRING)
    patrol_status = models.CharField('patrol status', max_length=MIN_STRING, null=True, choices=PatrolStatus.choices,
                                     default=PatrolStatus.CREATION)
    description = models.TextField('description', max_length=MAX_STRING, null=True)
    time_created = models.DateTimeField('time created', default=now)
    time_updated_last = models.DateTimeField('last updated', default=now)
    # TODO: update location options based on api in 'get_locations' function
    location = models.CharField(max_length=MEDIUM_STRING, choices=get_locations())
    date = models.DateField('date', default=now)
    start_time = models.TimeField('start time', default=now)
    end_time = models.TimeField('end time', default=now)
    # TODO update automatic priority based on api in 'get_priority' function
    priority = models.IntegerField('priority', default=get_priority())
    # TODO update automatic priority based on api in 'get_patrol_size' function
    participants_needed = models.IntegerField('participants needed', default=get_patrol_size())
    reactions = models.ManyToManyField(User, related_name='reactions', blank=True)
    approved_reactions = models.ManyToManyField(User, related_name='approved_reactions', blank=True)
    users_participated = models.ManyToManyField(User, related_name='participants', blank=True)

    def __str__(self):
        return f'title: {self.title} | location: {self.location} | priority: {self.priority} | ' \
               f'manager: {self.manager} | date: {self.date} | between: {self.start_time}-{self.end_time}'

    def get_absolute_url(self):
        return reverse('patrol', args=(str(self.pk),))

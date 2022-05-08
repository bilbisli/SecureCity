from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator
import datetime
from Patrols.models import get_locations
from django.db.models.signals import post_save
from django.dispatch import receiver

MEDIUM_STRING = 63

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    type = models.CharField(max_length=50, default='Parent')
    ID_Number = models.CharField(max_length=9, validators=[MinLengthValidator(9)])
    Phone_Number = models.CharField(max_length=10, validators=[MinLengthValidator(10)])
    Birthday = models.DateField(default=datetime.date.today)
    First_Name = models.CharField(validators=[MinLengthValidator(2)], max_length=50)
    Last_Name = models.CharField(validators=[MinLengthValidator(2)], max_length=50)
    models.CharField(max_length=MEDIUM_STRING, choices=get_locations())
    City = models.CharField(default='Beer Sheba', validators=[MinLengthValidator(2)], max_length=50)
    Neighborhood = models.CharField(max_length=MEDIUM_STRING, choices=get_locations())
    is_patrol_manager = models.BooleanField(default=False)

    def setPatrolManager(self):
        self.is_patrol_manager = True
        self.save()

    def getPatrolManager(self):
        return self.is_patrol_manager

    def get_fields_values(self):
        return [(field.name, field.value_to_string(self)) for field in Parent._meta.fields]

    def __str__(self):
        return f"{self.user.username}'s profile"


# UserProfile is created automatically when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Parent.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

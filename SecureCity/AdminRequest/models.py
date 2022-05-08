from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

MAX_STRING = 150


class AdminRequest(models.Model):
    userAsked = models.OneToOneField(User, on_delete=models.CASCADE, null=False, primary_key=True)
    date = models.DateField('date', default=timezone.now, null=False)
    description = models.TextField('description', max_length=MAX_STRING, null=True, blank=True)

    @classmethod
    def create(cls, currentUser, description):
        UserReuest = cls(userAsked=currentUser, description=description)
        return UserReuest

    def get_fields_values(self):
        return [(field.name, field.value_to_string(self)) for field in AdminRequest._meta.fields]

    def get_userAsked(self):
        return self.userAsked

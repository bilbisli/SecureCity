from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

MAX_STRING = 1023

class AdminRequest(models.Model):
    userAsked = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    date = models.DateField('date', default=timezone.localtime(timezone.now()), null=False)
    description = models.TextField('description', max_length=MAX_STRING, null=True, blank=True)
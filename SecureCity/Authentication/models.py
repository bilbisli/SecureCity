from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator
import datetime

numeric = RegexValidator(r'^[0-9+]', 'Only digit characters.')

class Parent(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    type=models.CharField(max_length=50,default='Parent')
    ID_Number = models.CharField(max_length=9, validators=[MinLengthValidator(9)])
    Phone_Number = models.CharField(max_length=10,validators=[numeric,MinLengthValidator(10)])
    Birthday = models.DateField(default=datetime.date.today)
    First_Name = models.CharField(validators=[MinLengthValidator(2)],max_length=50)
    Last_Name = models.CharField(validators=[MinLengthValidator(2)],max_length=50)
    neighborhood_CHOICES = (
        ('1', 'Neve Zeev'), ('2', 'Neot Lon')
    )
    City = models.CharField(validators=[MinLengthValidator(2)],max_length=50)
    Neighborhood = models.CharField(default='', choices=neighborhood_CHOICES,max_length=50)
    def __str__(self):
        return self.user.username


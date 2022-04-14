from django.db import models
MEDIUM_STRING = 63

class Contact(models.Model):
    name = models.CharField('name', max_length=MEDIUM_STRING)
    telephone = models.CharField('telephone', max_length=MEDIUM_STRING)

    def __str__(self):
        return self.name

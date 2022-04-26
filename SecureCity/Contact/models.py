from django.db import models
MEDIUM_STRING = 63

class Contact(models.Model):
    name = models.CharField('name', max_length=MEDIUM_STRING)
    telephone = models.CharField('telephone', max_length=MEDIUM_STRING)

    def get_fields_values(self):
        return [(field.name, field.value_to_string(self)) for field in Contact._meta.fields]

    def __str__(self):
        return self.name

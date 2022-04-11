from django import forms
from .models import Patrol, User


class PatrolForm(forms.ModelForm):
    class Meta:
        model = Patrol
        fields = [
            'title',
            'location',
            'priority',
            'participants needed',
            'date',
            'start_time',
            'end_time',
            'description',
            'patrol_status',
        ]
        exclude = ['manager', 'time_created', 'time_updated_last', ]

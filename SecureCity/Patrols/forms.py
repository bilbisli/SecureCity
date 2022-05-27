
from django import forms
from django.utils.dateparse import parse_date, parse_time

from .models import Patrol, User, current_time


class PatrolForm(forms.ModelForm):
    class Meta:
        model = Patrol
        fields = [
            'title',
            'location',
            'priority',
            'participants_needed',
            'date',
            'start_time',
            'end_time',
            'description',
            'patrol_status',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        # date = forms.DateField(widget=forms.SelectDateWidget(
        #
        # ), )
        exclude = ['time_created', 'time_updated_last']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.stat = kwargs.pop('stat', None)
        super(PatrolForm, self).__init__(*args, **kwargs)

    def clean_date(self):
        # Check if the date is in the past
        date = self.cleaned_data.get('date')
        if self.stat != 'edit':
            if date < current_time().date():
                raise forms.ValidationError("Date cannot be in the past")
        return date

    def clean(self):
        if self.stat != 'edit':
            cleaned_data = super().clean()  # Call the parent clean method
            date = cleaned_data.get('date')
            start_time = cleaned_data.get('start_time')
            end_time = cleaned_data.get('end_time')

            if start_time >= end_time:
                self.add_error('start_time', 'Start time must be before end time')

            # check if the start time is in the past
            if date == current_time().date() and start_time < current_time().time():
                self.add_error('start_time', "Start time cannot be in the past - change the date/time")
            patrols = self.user.patrols.all()
            for patrol in patrols:
                if date == patrol.date:
                    if patrol.start_time <= start_time <= patrol.end_time \
                            or patrol.start_time <= end_time <= patrol.end_time\
                            or start_time <= patrol.start_time <= end_time:
                        raise forms.ValidationError({"date": "You already have a patrol on this date at this time"})

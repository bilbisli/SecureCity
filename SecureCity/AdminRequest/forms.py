from django import forms
from .models import AdminRequest
from django.utils import timezone

def current_time():
    return timezone.localtime(timezone.now())

class AdminRequstForm(forms.ModelForm):
    class Meta:
        model = AdminRequest
        fields = [
                'userAsked',
                'date',
                'description'
        ]
        widgets = {
        'date': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date > current_time().date():
            raise forms.ValidationError("Date cannot be in the future")
        return date
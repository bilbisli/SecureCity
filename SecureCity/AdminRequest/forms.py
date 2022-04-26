from django import forms
from .models import AdminRequest

class AdminRequstForm(forms.ModelForm):
    class Meta:
        model = AdminRequest
        fields = [
                'userAsked',
                'date',
                'description'
        ]

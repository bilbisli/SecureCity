from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Parent
from django.forms.widgets import SelectDateWidget
from django.contrib.admin.widgets import AdminDateWidget
from datetime import date



class ExtendedUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','password1','password2',)

    def save(self,commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class ParentProfileForm(forms.ModelForm):
    error_css_class = 'error'
    class Meta:
        model=Parent
        fields = ('First_Name', 'Last_Name','Birthday','ID_Number','Phone_Number','City','Neighborhood')
        widgets = {
            'birthday': SelectDateWidget(years=range(1900, date.today().year + 1)),
        }
    def clean_ID_Number(self):
        ID_Number = self.cleaned_data['ID_Number']
        if not ID_Number.isdigit():
            raise forms.ValidationError("ID must contain numbers only")
        return ID_Number

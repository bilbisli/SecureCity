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
    def clean_Phone_Number(self):
        Phone_Number = self.cleaned_data['Phone_Number']
        if not Phone_Number.isdigit():
            raise forms.ValidationError("Phone Number must contain numbers only")
        return Phone_Number
    def clean_Birthday(self):
        Birthday = self.cleaned_data['Birthday']
        today = date.today()
        age = today.year - Birthday.year - ((today.month, today.day) < (Birthday.month, Birthday.day))
        if age < 18:
            raise forms.ValidationError("Sorry, you need to be at least 18 years old.")
        return Birthday
    def clean_Birthday(self):
        Birthday = self.cleaned_data['Birthday']
        today = date.today()
        age = today.year - Birthday.year - ((today.month, today.day) < (Birthday.month, Birthday.day))
        if age < 18:
            raise forms.ValidationError("Sorry, you need to be at least 18 years old.")
        return Birthday
    def clean_First_Name(self):
        First_Name = self.cleaned_data['First_Name']
        if not First_Name.isalpha():
            raise forms.ValidationError("First name must contain letters only")
        return First_Name
    def clean_Last_Name(self):
        Last_Name = self.cleaned_data['Last_Name']
        if not Last_Name.isalpha():
            raise forms.ValidationError("Last name must contain letters only")
        return Last_Name
    def clean_City(self):
        City = self.cleaned_data['City']
        city2 = City.replace(' ','')
        if not city2.isalpha():
            raise forms.ValidationError("City must contain letters only")
        return City


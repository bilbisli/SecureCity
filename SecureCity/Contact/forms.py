from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
                'name',
                'telephone'
        ]
    def clean_name(self):
        Name = self.cleaned_data['name']
        if not Name.isalpha():
            raise forms.ValidationError("Name must contain letters only")
        return Name

    def clean_telephone(self):
        Phone_Number = self.cleaned_data['telephone']
        if not Phone_Number.isdigit():
            raise forms.ValidationError("Phone Number must contain numbers only")
        if not len(Phone_Number)==10:
            raise forms.ValidationError("Phone Number must contain 10 digits")
        return Phone_Number
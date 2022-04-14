from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import Contact


def contact_management(request):
    contacts = Contact.objects.all()
    context = {
            'contacts': contacts
    }
    return render(request, 'HomePage/ContactPage.html', context)

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import Contact
from SecureCity.Authentication.models import Parent
from .forms import ContactForm
from django.shortcuts import redirect


def contact_management(request):
    contacts = Contact.objects.all()
    patrols = Parent.objects.filter(is_patrol_manager=True)
    context = {
        'contacts': contacts,
        'patrols': patrols
    }
    return render(request, 'HomePage/ContactPage.html', context)


def createContact(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact = contact_form.instance
            form = contact_form.save()
            return redirect('adminPage')
    else:
        contact_form = ContactForm()
    context = {
        'form': contact_form,
    }
    return render(request, 'HomePage/CreateContact.html', context)

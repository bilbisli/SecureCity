from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import Contact
from Authentication.models import Parent


def contact_management(request):
    contacts = Contact.objects.all()
    patrols = Parent.objects.filter(is_patrol_manager=True)
    context = {
            'contacts': contacts,
            'patrols': patrols
    }
    return render(request, 'HomePage/ContactPage.html', context)

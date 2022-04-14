from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import Contact


# @user_passes_test(lambda u: u.is_authenticated and u.profile.is_superuser, login_url='/', redirect_field_name=None)
# def contact_management(request):
#     contacts = Contact.objects.all()
#     context = {
#             'contacts': contacts
#     }
#     return render(request, 'HomePage/ContactPage.html', context)

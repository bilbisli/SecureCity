from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponse

from HomePage.forms import ContactForm
from HomePage.forms import PatrolForm
from .models import *


@login_required(login_url='/Login/')
def home(request):
    return render(request, 'HomePage/homePage.html')


@user_passes_test(lambda u: u.is_authenticated and u.profile.is_patrol_manager, login_url='/', redirect_field_name=None)
def patrol_management(request):
    patrols = [(number + 1, patrol) for number, patrol in enumerate(request.user.patrols.all())]
    context = {
            'patrols': patrols
    }
    return render(request, 'Patrols/PatrolManagement.html', context)


@user_passes_test(lambda u: u.is_authenticated and u.profile.is_patrol_manager, login_url='/', redirect_field_name=None)
def create_patrol(request):
    if request.method == 'POST':
        patrol_form = PatrolForm(request.POST or None, user=request.user)
        if patrol_form.is_valid():
            patrol = patrol_form.instance
            patrol.manager = request.user
            form = patrol_form.save()
            return patrol_management(request)
    else:
        patrol_form = PatrolForm()
    context = {
        'form': patrol_form,
    }
    return render(request, 'Patrols/CreatePatrol.html', context)

@login_required(login_url='/Login/')
def parent_patrol(request):
    patrols = Patrol.objects.all()
    context = {
            'patrols': patrols
    }
    return render(request, 'Patrols/ParentPatrolPage.html', context)

@user_passes_test(lambda u: u.is_authenticated and u.profile.is_patrol_manager, login_url='/', redirect_field_name=None)
def contact_management(request):
    contacts = Contact.objects.all()
    context = {
            'contacts': contacts
    }
    return render(request, 'HomePage/ContactPage.html', context)
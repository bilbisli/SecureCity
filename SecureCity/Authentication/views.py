from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import ExtendedUserCreationForm, ParentProfileForm
from Patrols import models as PatrolModels


def AddParent(request):
    admin = False
    if "admin" in request.GET:
        admin = True
    if request.method == 'POST':
        admin = request.POST.get('clicked')
        form = ExtendedUserCreationForm(request.POST)
        profile_form = ParentProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            user.profile.delete()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            if admin == 'False':
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect("homepage")
            else:
                return redirect("adminPage")
        else:
            return render(request, 'Authentication/AddParent.html',
                          {'form': form, 'profile_form': profile_form, 'error': "Bad Data Please Try Again",
                           'admin': admin})
    else:
        form = ExtendedUserCreationForm()
        profile_form = ParentProfileForm()
    context = {'form': form, 'profile_form': profile_form, 'error': "", 'admin': admin}
    return render(request, 'Authentication/AddParent.html', context)


def logoutuser(request):
    logout(request)
    return redirect('homepage')


def loginU(request):
    if not User.objects.filter(is_superuser=True).first():
        user = User.objects.create(
            username='admin',
            is_superuser=True,
        )
        user.set_password('123456')
        user.save()
    if request.method == 'GET':
        return render(request, 'Authentication/Login.html', {'form': AuthenticationForm(), 'error': ""})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'Authentication/Login.html',
                          {'form': AuthenticationForm(), 'error': "Wrong username or password"})
        else:
            login(request, user)
            return redirect('homepage')


def residentPage(request):
    objects = PatrolModels.Patrol.objects.filter(manager=request.user)
    fields = PatrolModels.Patrol._meta.get_fields()[:-3]
    type = "patrol"
    context = {
        'objects': objects,
        'fields': fields,
        'type': type
    }
    return render(request, 'Authentication/residentPage.html', context)

import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import ExtendedUserCreationForm, ParentProfileForm
from Patrols import models as PatrolModels
from adminPage.models import get_data, updateData


crime_columns = (
        'עבירות כלפי המוסר', 'עבירות כלפי הרכוש', 'עבירות נגד גוף', 'עבירות סדר ציבורי', 'עבירות מין',
        'עבירות נגד אדם',)


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
        updateData()
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
    patrols = PatrolModels.Patrol.objects.filter(approved_reactions__profile__user__id=request.user.id)
    fields = PatrolModels.Patrol._meta.get_fields()[:-3]
    context = {
        'patrols': patrols,
        'fields': fields
    }
    if request.user.profile.is_patrol_manager:
        neighborhood_column = "neighborhood_1"
        heb_neighb_col = "שכונה"
        total_population_col = "סה''כ"
        columns = [heb_neighb_col, total_population_col] + list(crime_columns)
        df = get_data('unified_data')
        if df is not None:

            if not request.user.is_superuser:
                df = df[df[neighborhood_column] == request.user.profile.Neighborhood]

            df[heb_neighb_col] = df[neighborhood_column]
            df = df.drop(neighborhood_column, axis=1)
            df = df[columns]
            df = df.groupby([heb_neighb_col]).sum()
            # df.to_excel('static/data.xlsx')

        objects = PatrolModels.Patrol.objects.filter(manager=request.user)
        p_type = "patrol"
        context2 = {
            'objects': objects,
            'p_type': p_type,
            'df': df
        }
        context.update(context2)
    return render(request, 'Authentication/residentPage.html', context)

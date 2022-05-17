from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
#import pandas as pd
from django.contrib.auth.models import User


@login_required(login_url='/Login/')
def home(request):
    if not User.objects.filter(is_superuser=True).first():
        user = User.objects.create(
            username='admin',
            is_superuser=True,
        )
        user.set_password('123456')
        user.save()
    return render(request, 'HomePage/homePage.html')

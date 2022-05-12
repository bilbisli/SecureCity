from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
#import pandas as pd


@login_required(login_url='/Login/')
def home(request):
    return render(request, 'HomePage/homePage.html')

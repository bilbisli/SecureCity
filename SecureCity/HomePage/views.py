from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'HomePage/homePage.html')


def patrol_management_page(request):
    return render(request, 'PatrolManagement/PatrolManagement.html')


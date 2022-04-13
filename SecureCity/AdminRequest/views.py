from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .models import AdminRequest


def becomePatrolManager(request):
    if request.method == "GET":
        return render(request, 'AdminRequest/becomePatrolManager.html')
    else:
        newRequest = AdminRequest.create(request.user, request.POST['text'])
        newRequest.save()
        return render(request, 'HomePage/homePage.html')

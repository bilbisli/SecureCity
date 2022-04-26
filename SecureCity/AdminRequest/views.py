from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .models import AdminRequest
from .forms import AdminRequstForm

def becomePatrolManager(request):
    if request.method == "GET":
        return render(request, 'AdminRequest/becomePatrolManager.html')
    else:
        newRequest = AdminRequest.create(request.user, request.POST['text'])
        newRequest.save()
        return render(request, 'HomePage/homePage.html')


def CreateRequest(request):
    if request.method == 'POST':
        request_form = AdminRequstForm(request.POST)
        if request_form.is_valid():
            req = request_form.instance
            form = request_form.save()
            return redirect('adminPage')
    else:
        request_form = AdminRequstForm()
    context = {
        'form': request_form,
    }
    return render(request, 'AdminRequest/CreateRequest.html', context)
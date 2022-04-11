from django.shortcuts import render, redirect
from django.http import HttpResponse

from HomePage.forms import PatrolForm


def home(request):
    return render(request, 'HomePage/homePage.html')


# TODO: limit access to this page to only area managers
def patrol_management(request):
    patrols = [(number + 1, patrol) for number, patrol in enumerate(request.user.patrols.all())]
    context = {
            'patrols': patrols
    }
    return render(request, 'Patrols/PatrolManagement.html', context)


# TODO: limit access to this page to only area managers
def create_patrol(request):
    if request.method == 'POST':
        patrol_form = PatrolForm(request.POST or None)
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

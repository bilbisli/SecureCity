import pandas as pd
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render
from .forms import PatrolForm
from .models import Patrol


def patrol_page(request, patrol_id):
    try:
        patrol = Patrol.objects.get(id=patrol_id)
    except Patrol.DoesNotExist:
        raise Http404(f"Invalid patrol id: {patrol_id}")
    context = {
        'patrol': patrol,
    }
    return render(request, 'Patrols/PatrolPage.html', context)


@user_passes_test(lambda u: u.is_authenticated and u.profile.is_patrol_manager, login_url='/', redirect_field_name=None)
def patrol_management(request):
    error = ''
    if request.POST:
        patrols = Patrol.objects.filter(id__in=request.POST.getlist("ToCSV"))
        if not len(patrols):
            error = 'Please choose at least one Patrol!'
        else:
            titles = []
            locations = []
            priorities = []
            managers = []
            dates = []
            between = []
            for p in patrols:
                titles.append(p.title)
                locations.append(p.location)
                priorities.append(p.priority)
                managers.append(str(p.manager))
                dates.append(str(p.date))
                between.append(str(p.start_time)+'-'+str(p.end_time))
            csvFile = pd.DataFrame()
            csvFile['Title'] = titles
            csvFile['Location'] = locations
            csvFile['Priority'] = priorities
            csvFile['Manager'] = managers
            csvFile['Date'] = dates
            csvFile['Time'] = between
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=Patrols_Summary.csv'
            csvFile.to_csv(path_or_buf=response)
            return response

    patrols = [(number + 1, patrol) for number, patrol in enumerate(request.user.patrols.all())]
    context = {
            'patrols': patrols,
            'error': error
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
    if request.GET.get('sort') == 'Priority':
        activePatrols = Patrol.objects.filter(patrol_status__in=["Creation", "Active"]).order_by('-priority')
        donePatrols = Patrol.objects.filter(patrol_status="Archive").order_by('-priority')
    else:
        activePatrols = Patrol.objects.filter(patrol_status__in=["Creation", "Active"])
        donePatrols = Patrol.objects.filter(patrol_status="Archive")
    context = {
        'activePatrols': activePatrols,
        'donePatrols': donePatrols
    }
    return render(request, 'Patrols/ParentPatrolPage.html', context)

import pandas as pd
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from datetime import datetime
from .forms import PatrolForm
from .models import Patrol, get_locations
from django.db.models import Q
from adminPage.models import get_data
from adminPage.views import unify_data


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
                between.append(str(p.start_time) + '-' + str(p.end_time))
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
    if request.user.is_superuser:
        patrols = [(number + 1, patrol) for number, patrol in enumerate(Patrol.objects.all())]
    else:
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
            return redirect('PatrolManagement')
    else:
        patrol_form = PatrolForm()
    context = {
        'form': patrol_form,
    }
    analyze_patrols_priority()
    return render(request, 'Patrols/CreatePatrol.html', context)


@login_required(login_url='/Login/')
def parent_patrol(request):
    if request.GET.get('sort') == 'Priority':
        activePatrols = Patrol.objects.filter(patrol_status__in=["Creation", "Active"]).order_by('-priority')
        donePatrols = Patrol.objects.filter(patrol_status="Archive").order_by('-priority')
    elif request.GET.get('sort') == 'Participants_Needed':
        activePatrols = Patrol.objects.filter(patrol_status__in=["Creation", "Active"]).order_by('-participants_needed')
        donePatrols = Patrol.objects.filter(patrol_status="Archive").order_by('-participants_needed')
    elif request.GET.get('sort') == 'Location':
        activePatrols = Patrol.objects.filter(location=request.user.profile.Neighborhood)
        donePatrols = Patrol.objects.filter(patrol_status="Archive").filter(location=request.user.profile.Neighborhood)

    else:
        activePatrols = Patrol.objects.filter(patrol_status__in=["Creation", "Active"])
        donePatrols = Patrol.objects.filter(patrol_status="Archive")

    if request.method == 'POST':
        if request.POST.get('STime') and request.POST.get('STime') != '0':
            sTime = datetime.strptime(request.POST.get('STime'), '%H:%M').time()
            activePatrols = list(activePatrols)
            activePatrols = list(filter(lambda x: x.start_time >= sTime, activePatrols))
        if request.POST.get('ETime') and request.POST.get('ETime') != '0':
            eTime = datetime.strptime(request.POST.get('ETime'), '%H:%M').time()
            activePatrols = list(activePatrols)
            activePatrols = list(filter(lambda x: x.start_time <= eTime, activePatrols))
        if request.POST.get("locationSelect"):
            if request.POST.get("locationSelect") == "הכל":
                activePatrols = Patrol.objects.filter(patrol_status__in=["Creation", "Active"])
                donePatrols = Patrol.objects.filter(patrol_status="Archive")
            else:
                activePatrols = list(activePatrols)
                activePatrols = list(filter(lambda x: x.location == request.POST.get("locationSelect"), activePatrols))
                donePatrols = list(donePatrols)
                donePatrols = list(filter(lambda x: x.location == request.POST.get("locationSelect"), donePatrols))
    locations = ("הכל",) + tuple(location[0] for location in get_locations())
    context = {
        'activePatrols': activePatrols,
        'donePatrols': donePatrols,
        'locations': locations,
    }
    return render(request, 'Patrols/ParentPatrolPage.html', context)


def analyze_patrols_priority(parameters=('עבירות כלפי המוסר', 'עבירות כלפי הרכוש', 'עבירות נגד גוף', 'עבירות סדר ציבורי', 'עבירות מין', 'עבירות נגד אדם',)):
    data_df = get_data()
    neighborhood_table = 'stat_n-hoods_table'
    neighborhood_column = 'neighborhood_1'
    stat_area_column = 'stat-area'
    heb_stat_area_column = "אג''ס"
    total_offenses_column = 'total_offenses'
    heb_total_residents_column = "סה''כ"
    total_residents_column = 'total_residents'
    areas_df = get_data(neighborhood_table)

    # take care of the case where there is no data in the database
    if not areas_df or not data_df:
        return None

    neighbourhoods = areas_df[neighborhood_column].unique()

    data_df[total_offenses_column] = data_df[list(parameters)].sum(axis=1)
    # data_df.to_excel('static/offenses.xlsx', index=False)
    
    # locations = [location[0] for location in get_locations()]
    data_df[stat_area_column] = data_df[heb_stat_area_column]
    data_df[total_residents_column] = data_df[heb_total_residents_column]
#      סה''כ
    unified_data = unify_data(areas_df[[neighborhood_column, stat_area_column]],
               data_df[[stat_area_column, total_offenses_column, total_residents_column]], on_column=stat_area_column)

    neighborhoods_df = unified_data.groupby(neighborhood_column).sum()
    neighborhoods_df['residents_offense_ratio'] = neighborhoods_df[total_residents_column] / neighborhoods_df[total_offenses_column]
    # neighborhoods_df.to_excel('static/neighb_offenses.xlsx')


    # unified_data.to_excel('static/uni_d.xlsx', index=False)


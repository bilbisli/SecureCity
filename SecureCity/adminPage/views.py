import pandas as pd
import requests
from django.shortcuts import render
from Authentication import models as AuthModels
from AdminRequest import models as AdminModels
from Contact import models as ContactModels
from Patrols import models as PatrolModels
from Authentication import forms as Authforms
from Contact import forms as ContactForms
from Patrols import forms as PartolForms
from AdminRequest import forms as AdminRequestForms
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import update_data, DataFile, organize_primary_and_backup_data


@user_passes_test(lambda u: u.is_superuser, login_url='/', redirect_field_name=None)
def adminP(request, msg=''):
    objects = ''
    fields = ''
    type = ''
    req_msg = request.session.get('msg')
    msg = req_msg if msg == '' and req_msg else msg
    if req_msg:
        del request.session['msg']

    if request.POST:
        if "users" in request.POST:
            objects = AuthModels.Parent.objects.all()
            fields = AuthModels.Parent._meta.get_fields()
            type = "user"

        if "patrols" in request.POST:
            objects = PatrolModels.Patrol.objects.all()
            fields = PatrolModels.Patrol._meta.get_fields()[:-3]
            type = "patrol"

        if "contacts" in request.POST:
            objects = ContactModels.Contact.objects.all()
            fields = ContactModels.Contact._meta.get_fields()
            type = "contact"

        if "requests" in request.POST:
            objects = AdminModels.AdminRequest.objects.all()
            fields = AdminModels.AdminRequest._meta.get_fields()
            type = "request"

    context = {
        'objects': objects,
        'fields': fields,
        'type': type,
        'msg': msg
    }
    return render(request, 'adminPage/AdminPage.html', context)


@user_passes_test(lambda u: u.is_superuser or u.profile.is_patrol_manager, login_url='/', redirect_field_name=None)
def adminEdit(request):
    form = ''
    if "EditObject" in request.GET:
        obj = request.GET.get('EditObject')
        if "user" in obj:
            obj = obj.replace("user", '')
            obj = get_object_or_404(AuthModels.Parent, id=obj)
            form = Authforms.ParentProfileForm(request.POST or None, instance=obj)
        elif "request" in obj:
            obj = obj.replace("request", '')
            originalUserID = obj
            obj = get_object_or_404(AdminModels.AdminRequest, userAsked__id=obj)
            form = AdminRequestForms.AdminRequstForm(request.POST or None, instance=obj)
            if form.is_valid() and originalUserID != form.cleaned_data['userAsked']:
                form.save()
                delObj = get_object_or_404(AdminModels.AdminRequest, userAsked__id=originalUserID)
                delObj.delete()
                return redirect('adminPage')
        elif "contact" in obj:
            obj = obj.replace("contact", '')
            obj = get_object_or_404(ContactModels.Contact, id=obj)
            form = ContactForms.ContactForm(request.POST or None, instance=obj)
        elif "patrol" in obj:
            obj = obj.replace("patrol", '')
            obj = get_object_or_404(PatrolModels.Patrol, id=obj)
            form = PartolForms.PatrolForm(request.POST or None, instance=obj, stat='edit')
        if form.is_valid():
            form.save()
            return redirect('adminPage')
    elif "patrol" in request.GET:
        obj = request.GET.get('patrol')
        if "user" in obj:
            obj = obj.replace("user", '')
            obj = get_object_or_404(AuthModels.Parent, id=obj)
            if obj.is_patrol_manager:
                obj.is_patrol_manager = False
            else:
                obj.setPatrolManager()
            obj.save()
            return redirect('adminPage')

    context = {
        "form": form
    }
    return render(request, 'adminPage/AdminEdit.html', context)


@user_passes_test(lambda u: u.is_superuser, login_url='/', redirect_field_name=None)
def adminDelete(request):
    form = ''
    if "DeleteObject" in request.GET:
        obj = request.GET.get('DeleteObject')
        if "user" in obj:
            obj = obj.replace("user", '')
            obj = get_object_or_404(AuthModels.Parent, id=obj)
            obj = obj.user
            if obj == request.user:
                return redirect('adminPage')
        elif "request" in obj:
            obj = obj.replace("request", '')
            obj = get_object_or_404(AdminModels.AdminRequest, userAsked__id=obj)
        elif "contact" in obj:
            obj = obj.replace("contact", '')
            obj = get_object_or_404(ContactModels.Contact, id=obj)
        elif "patrol" in obj:
            obj = obj.replace("patrol", '')
            obj = get_object_or_404(PatrolModels.Patrol, id=obj)
        obj.delete()
    return redirect('adminPage')


@user_passes_test(lambda u: u.is_superuser, login_url='/', redirect_field_name=None)
def adminApprove(request):
    form = ''
    if "ApproveObject" in request.GET:
        obj = request.GET.get('ApproveObject')
        if "request" in obj:
            obj = obj.replace("request", '')
            obj = get_object_or_404(AdminModels.AdminRequest, userAsked__id=obj)
            UserObj = get_object_or_404(AuthModels.Parent, user=obj.get_userAsked())
            UserObj.setPatrolManager()
            obj.delete()
    return redirect('adminPage')


def parentsRequests(request):
    if "ApproveObject" in request.GET:
        obj = request.GET.get('ApproveObject')
        obj = get_object_or_404(AdminModels.AdminRequest, userAsked__id=obj)
        UserObj = get_object_or_404(AuthModels.Parent, user=obj.get_userAsked())
        UserObj.setPatrolManager()
        obj.delete()
    elif "DeleteObject" in request.GET:
        obj = request.GET.get('DeleteObject')
        obj = get_object_or_404(AdminModels.AdminRequest, userAsked__id=obj)
        obj.delete()
    requests = AdminModels.AdminRequest.objects.all()
    fields = AdminModels.AdminRequest._meta.get_fields()
    context = {
        'requests': requests,
        'fields': fields
    }
    return render(request, 'adminPage/ParentsRequests.html', context)


@user_passes_test(lambda u: u.is_superuser, login_url='/', redirect_field_name=None)
def updateDatabases(request):
    # Update the stat-area database
    statistical_areas_df = update_data(data_name='stat_n-hoods_table',
                                       api_endpoint='https://opendataprod.br7.org.il/api/3/',
                                       # api_url='action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e')
                                       data_packages_search_path='action/package_search?q=',
                                       data_search_path='action/datastore_search?resource_id=',
                                       )
    print(statistical_areas_df)

    # Update the demographic database
    unified_demographics = update_data(data_name='demographics',
                                       api_endpoint='https://opendataprod.br7.org.il/api/3/',
                                       # api_url='action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e')
                                       data_packages_search_path='action/package_search?q=',
                                       data_search_path='action/datastore_search?resource_id=',
                                       df_preprocessing_function=demographic_tables_build,
                                       to_df=False,
                                       save=False,
                                       )

    # Update the crime database
    crime_rates_df = update_data(data_name='crime_records_data',
                                 api_endpoint='https://data.gov.il/api/3/',
                                 # api_url='action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e')
                                 data_packages_search_path='action/package_search?q=',
                                 data_search_path='action/datastore_search?resource_id=',
                                 df_preprocessing_function=crime_df_clean,
                                 )

    lamas_demographics = pd.read_csv('static/lamas_simplified.csv')
    lamas_demographics = lamas_demographics.iloc[2:, :-1]
    lamas_demographics["אג''ס"] = lamas_demographics["אג''ס"].astype(int)
    unified_data = unify_data(lamas_demographics, unified_demographics, crime_rates_df.load_frame(), on_column="אג''ס")
    organize_primary_and_backup_data('unified_data')
    DataFile.put_frame(data_frame=unified_data, file_name='unified_data', is_primary=True)

    request.session['msg'] = "Successfully updated databases"
    return redirect('adminPage')


def crime_df_clean(df, city_query='באר שבע'):
    df = df[df['Settlement_Council'] == city_query]
    df = df[df['StatArea'].notna() & df['StatisticCrimeGroup'].notna()]
    df['StatArea'] = [int(stat_number) % 1000 for stat_number in df['StatArea']]
    crime_rates_df = pd.DataFrame()
    for stat_area in df['StatArea'].unique():
        temp_d = {"אג''ס": stat_area}
        for crime_category in df['StatisticCrimeGroup'].unique():
            count_pairs = len(df[(df['StatisticCrimeGroup'] == crime_category) & (
                    df['StatArea'] == stat_area)])
            temp_d[crime_category] = count_pairs
        crime_rates_df = pd.concat([crime_rates_df, pd.DataFrame.from_records([temp_d])], ignore_index=True)

    for crime_category in crime_rates_df:
        crime_rates_df[crime_category] = crime_rates_df[crime_category].astype(int)
    crime_rates_df["אג''ס"] = crime_rates_df["אג''ס"].astype(int)

    return crime_rates_df


def demographic_tables_build(df):
    unified_demographics = pd.read_csv('static/lamas_simplified.csv')
    unified_demographics = unified_demographics.drop(columns=unified_demographics.columns[-1:]).drop(
        columns=unified_demographics.columns[0])

    for table in filter(lambda r: r['format'] == 'JSON', df):
        # table_name = 'דמוגרפיה-' + table['name'].replace(' - JSON', "")
        temp_table = pd.DataFrame.from_records(requests.get(table['url']).json())
        unified_demographics = unify_data(unified_demographics, temp_table, on_column="אג''ס")

    unified_demographics["אג''ס"] = unified_demographics["אג''ס"].astype(int)

    data_name = 'unified_demographics'
    organize_primary_and_backup_data(data_name)
    DataFile.put_frame(data_frame=unified_demographics, file_name=data_name, is_primary=True)

    return unified_demographics


def unify_data(*data_frames, on_column):
    unified_data = data_frames[0]
    for df in data_frames:
        unified_data = pd.merge(unified_data, df, on=on_column, suffixes=('', '_y'))
        unified_data.drop(unified_data.filter(regex='_y$').columns.tolist(), axis=1, inplace=True)
    return unified_data

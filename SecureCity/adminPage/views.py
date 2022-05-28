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
from .models import updateData
from Patrols.models import get_patrol_size


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
    context = {}
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
            patrol = form.instance
            patrol.update_priority = True
            context['user_location'] = patrol.location[0] if type(patrol.location) == tuple else patrol.location
            context['recommended_people_num'] = get_patrol_size(patrol.location)

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

    context["form"] = form
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
    updateData()
    # unified_data.to_excel('static/unified_data.xlsx')

    request.session['msg'] = "Successfully updated databases"
    return redirect('adminPage')


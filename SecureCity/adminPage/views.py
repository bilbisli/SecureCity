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
from .models import update_data


@user_passes_test(lambda u: u.is_superuser, login_url='/', redirect_field_name=None)
def adminP(request, msg=''):
    objects = ''
    fields = ''
    type = ''

    req_msg = request.session.get('msg')
    print(req_msg)
    msg = req_msg if msg == '' and req_msg else msg

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
    return render(request, 'AdminPage/AdminPage.html', context)


@user_passes_test(lambda u: u.is_superuser, login_url='/', redirect_field_name=None)
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
    context = {
        "form": form
    }
    return render(request, 'AdminPage/AdminEdit.html', context)


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
def updateDatabases(request):
    update_data(data='crime')
    request.session['msg'] = "Successfully updated databases"
    return redirect('adminPage')


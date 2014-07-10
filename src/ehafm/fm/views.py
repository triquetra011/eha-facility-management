__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

import jsonfield

from fm.forms import AreaForm
from fm.models import Area

from fm.forms import FacilityForm
from fm.models import Facility

from fm.forms import ContactForm
from fm.models import Contact

from fm.forms import RoleForm
from fm.models import Role


@login_required(login_url='/login')
@staff_member_required
def home_view(request):
    return render(request, 'home.html')


@login_required(login_url='/login')
@staff_member_required
def areas_view(request):
    return render(request, 'areas.html', {'areas': Area.objects.all()})


@login_required(login_url='/login')
@staff_member_required
def add_new_area_view(request):
    form = AreaForm()
    if request.method == 'POST':
        form = AreaForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/fm/areas/')
    return render(request, 'add_new_area.html', {'form': form})


@login_required(login_url='/login')
@staff_member_required
def facilities_view(request):
    return render(request, 'facilities.html',
                  {'facilities': Facility.objects.all()})


@login_required(login_url='/login')
@staff_member_required
def add_new_facility_view(request):
    form = FacilityForm()
    if request.method == 'POST':
        form = FacilityForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/fm/facilities/')
    return render(request, 'add_new_facility.html', {'form': form})


@login_required(login_url='/login')
@staff_member_required
def facility_view(request, facility_id):
    # prepare a URL to the JSON document for this facility by substituting
    # 'json' for 'view' in the current URL
    json_url = reverse(facility_view, args=[facility_id])
    json_url = json_url.rsplit('/', 1)[0] + '/json'
    return render(request, 'facility.html',
                  {
                      'facility': Facility.objects.get(pk=facility_id),
                      'json_url': json_url,
                  })


@login_required(login_url='/login')
@staff_member_required
def contacts_view(request):
    return render(request, 'contacts.html',
                  {'contacts': Contact.objects.all()})


@login_required(login_url='/login')
@staff_member_required
def add_new_contact_view(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/fm/contacts/')
    return render(request, 'add_new_contact.html', {'form': form})


@login_required(login_url='/login')
@staff_member_required
def roles_view(request):
    return render(request, 'roles.html',
                  {'roles': Role.objects.all()})


@login_required(login_url='/login')
@staff_member_required
def add_new_role_view(request):
    form = RoleForm()
    if request.method == 'POST':
        form = RoleForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/fm/roles/')
    return render(request, 'add_new_role.html', {'form': form})


@login_required(login_url='/login')
@staff_member_required
def json_view(request, model_choice, container_id):
    model = None
    if model_choice == 'contacts':
        model = Contact
    elif model_choice == 'facilities':
        model = Facility
    container = model.objects.get(pk=container_id)
    json_document = jsonfield.JSONField().dumps_for_display(container.json)
    return HttpResponse(content=json_document,
                        content_type='application/json;charset=utf-8')


from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from ksda.models import *
from ksda.forms import NewFineForm

import json

@login_required
def routeToFinancesPage(request, originalContext):
    context = {}
    
    context['user'] = request.user
    brother = Brother.objects.get(user=request.user)
    context['brother'] = brother
    finingPower = brother.hasFiningPower()
    context['finingPower'] = finingPower
    
    if 'form' not in originalContext:
        context['form'] = NewFineForm()

    # Add fines to table
    context['fines'] = Fine.objects.all()

    # Add user fines to payment module
    context['userFines'] = Fine.objects.filter(brother=brother)

    # Get user's roles for fine creation form.
    context['roles'] = Role.objects.filter(brother=brother)
    context['GT'] = Role.objects.get(name='Grand Treasurer').brother

    context = dict(context.items() + originalContext.items())
    
    # Just display the finances table if this is a GET request
    if request.method == 'GET':
        return render(request, 'ksda/finances.html', context)
    
    return render(request, 'ksda/finances.html', context)

@login_required
def financesPage(request):
    context = {}
    return routeToFinancesPage(request, context)

@login_required
@transaction.atomic
def deleteFine(request):
    user = request.user
    if request.method != 'POST' or 'id' not in request.POST:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")

    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasFiningPower():
            return HttpResponse(json.dumps({}), content_type="application/json")
    except Brother.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")

    fineid = request.POST['id']
    try:
        fine = Fine.objects.get(id=fineid)
    except Fine.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")

    fine.delete()

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
@transaction.atomic
def completeFine(request):
    user = request.user
    if request.method != 'POST' or 'id' not in request.POST:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")

    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasFiningPower():
            return HttpResponse(json.dumps({}), content_type="application/json")
    except Brother.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")

    fineid = request.POST['id']
    try:
        fine = Fine.objects.get(id=fineid)
    except Fine.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")

    fine.completed = True
    fine.save()

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
@transaction.atomic
def newFine(request):
    context = {}
    user = request.user
    userBrother = Brother.objects.get(user=request.user)

    # Users without fining power should not be able to fine
    if not userBrother.hasFiningPower():
        context['dangerMessage'] = 'You do not have fining power.'
        return routeToFinancesPage(request, context)

    form = NewFineForm(data=request.POST)
    context['newFineForm'] = form

    # Validate the new fine and create it
    if not form.is_valid():
        context['dangerMessage'] = 'Error Creating Fine.'
        return routeToFinancesPage(request, context)

    if form.cleaned_data['chair'].brother != userBrother:
        context['dangerMessage'] = 'You are not that chair!'
        return routeToFinancesPage(request,context)

    fine = Fine.objects.create(reason=form.cleaned_data['reason'],
                               brother=form.cleaned_data['brother'],
                               assignedBy=userBrother,
                               amount=form.cleaned_data['amount'],
                               chair=form.cleaned_data['chair'])
    fine.save()
    context['successMessage'] = 'Fine Created.'

    return routeToFinancesPage(request,context)

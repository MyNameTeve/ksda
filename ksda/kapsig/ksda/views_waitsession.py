from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from ksda.models import *
from ksda.forms import *

import datetime
import json

days = 'mtwhf'

def loadWaitsessionWeekHTML(context, date=datetime.date.today()):
    brother = Brother.objects.get(user=context['user'])
    context['waitsessionPower'] = brother.hasWaitsessionPower()
    getWaitSessions(context, date)
    context['waitsessions_m'] = context['waitsessions'].filter(date__week_day=2)
    context['waitsessions_t'] = context['waitsessions'].filter(date__week_day=3)
    context['waitsessions_w'] = context['waitsessions'].filter(date__week_day=4)
    context['waitsessions_h'] = context['waitsessions'].filter(date__week_day=5)
    context['waitsessions_f'] = context['waitsessions'].filter(date__week_day=6)
    context['weekly_info'] = ''
    
    for d in days:
        if d == 'm':
            day = 'monday'
        elif d == 't':
            day = 'tuesday'
        elif d == 'w':
            day = 'wednesday'
        elif d == 'h':
            day = 'thursday'
        elif d == 'f':
            day = 'friday'

        context[day + '_info'] = "<h5> " + day.capitalize() + " </h5> "
        for waitsession in context['waitsessions_' + d]:
            button =  """
                      <button class='waitsessionDelete'> Delete </button>
                      <button class='waitsessionToggle'> %s </button> """ % \
                     ('&#10003' if waitsession.completed else 'Make Complete')
            
            if not context['waitsessionPower']:
                button = ''

            context[day + '_info'] += """
                <div class='row'>
                    <div class='%s' id='%s'> """ % \
                        (("bg-info" if waitsession.completed else "bg-danger"), \
                         str(waitsession.id)) 
            context[day + '_info'] += button + """
                        %s
                    </div>
                </div> """ % \
                         str(waitsession)

        # If no waitsessions exist for this day, display alt-text.
        if (not context['waitsessions_' + d]):
            context[day + '_info'] += """
                <div class="row">
                    <h5 class="bg-warning"> No assigned waitsession</h5>
                </div>        
                """
        context['weekly_info'] += context[day + '_info']

@login_required
def getUserInfo(request, originalContext):
    context = {}
    context['user'] = request.user
    loadWaitsessionWeekHTML(context)

    context['brothers'] = map(lambda ws: ws.displayInfo(), WaitsessionBrotherInfo.objects.filter(brother__active=True).order_by('brother__order'));

    if 'newWaitsessionForm' not in originalContext:
        context['newWaitsessionForm'] = NewWaitsessionForm()
    if 'newWaitunitForm' not in originalContext:
        context['newWaitunitForm'] = NewWaitunitForm()
    
    return dict(originalContext.items() + context.items())

def getWaitSessions(context, date):
    numericalDayOfWeek = date.isocalendar()[2] % 7
    start = (date + datetime.timedelta(-numericalDayOfWeek)) + datetime.timedelta(1)
    end = start + datetime.timedelta(4)

    context['start_date'] = str(start)
    context['end_date'] = str(end)
    context['waitsessions'] = Waitsession.objects.filter(date__range=[start, end]).order_by('date')


@login_required
def routeToPage(request, context):
    context = getUserInfo(request, context)
    return render(request, 'ksda/waitsessions.html', context)

@login_required
def waitsessionsPage(request):
    context = {}
    return routeToPage(request, context)

"""
AJAX Functions
"""
@login_required
@transaction.atomic
def toggleWaitsessionComplete(request):
    user = request.user
    if request.method != 'POST' or 'id' not in request.POST:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWaitsessionPower():
            return HttpResponse(json.dumps({}), content_type="application/json")
    except Brother.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")

    wsid = request.POST['id']
    waitsesh = Waitsession.objects.get(id=wsid)
    waitsesh.toggleComplete()
    waitsesh.save()
    waitsesh.brotherinfo.save()
    return HttpResponse(json.dumps({'units':str(waitsesh.brotherinfo.units)}), content_type="application/json")       

@login_required
@transaction.atomic
def deleteWaitsession(request):
    user = request.user
    if request.method != 'POST' or 'id' not in request.POST:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWaitsessionPower():
            return HttpResponse(json.dumps({}), content_type="application/json")
    except Brother.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")
  
    wsid = request.POST['id']
    try:
        waitsesh = Waitsession.objects.get(id=wsid)
    except Waitsession.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")       

    if (waitsesh.completed):
        waitsesh.toggleComplete()
        waitsesh.brotherinfo.save()

    units = str(waitsesh.brotherinfo.units)

    waitsesh.delete()

    return HttpResponse(json.dumps({'units':units}), content_type="application/json")       


@login_required
def getWaitsessionInfo(request):
    weekOffset = request.GET['weekOffset']
    date = datetime.date.today() + datetime.timedelta(7 * int(weekOffset))
    context = {}
    context['user'] = request.user
    loadWaitsessionWeekHTML(context, date)
    return HttpResponse(json.dumps(\
        {'weekly_info': context['weekly_info'], \
         'start_date' : context['start_date'], \
         'end_date':context['end_date']}) \
         , content_type="application/json") 

@login_required
@transaction.atomic
def addWaitsession(request):
    context = {}
    user = request.user

    if request.method != 'POST':
        # Error case
        return routeToPage(request, context)
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWaitsessionPower():
            return routeToPage(request, context)
    except Brother.DoesNotExist:
        # Error case
        return routeToPage(request, context)
 

    form = NewWaitsessionForm(data=request.POST, username=user.username)
    context['newWaitsessionForm'] = form

    if not form.is_valid():
        return routeToPage(request, context)
    
    ws = Waitsession.objects.create(date=form.cleaned_data['date'],
                                    brotherinfo=form.cleaned_data['brother'].waitsessionbrotherinfo)
    ws.save()

    context['successMessage'] = 'Waitsession Added.'
    
    return routeToPage(request, context)

@login_required
@transaction.atomic
def addWaitunit(request):
    context = {}
    user = request.user

    if request.method != 'POST':
        # Error case
        return routeToPage(request, context)
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWaitsessionPower():
            return routeToPage(request, context)
    except Brother.DoesNotExist:
        # Error case
        return routeToPage(request, context)
 

    form = NewWaitunitForm(data=request.POST, username=user.username)
    context['newWaitunitForm'] = form

    if not form.is_valid():
        return routeToPage(request, context)

    brother = Brother.objects.get(id=form.cleaned_data['brother'].id)
    oldUnits = brother.waitsessionbrotherinfo.units
    brother.waitsessionbrotherinfo.units += form.cleaned_data['newUnits']
    brother.waitsessionbrotherinfo.save()
    newUnits = brother.waitsessionbrotherinfo.units

    change = 'did not change'
    if oldUnits < newUnits:
        change = 'increased'
    elif oldUnits > newUnits:
        change = 'decreased'

    context['successMessage'] = 'Waitunits ' + change + ' for ' + \
                                brother.getName() + ', from ' + \
                                str(oldUnits) + ' to ' + str(newUnits)

    return routeToPage(request, context)

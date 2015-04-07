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

days = ['sat', 'sun']

def loadWorksessionWeekHTML(context, date=datetime.date.today()):
    brother = Brother.objects.get(user=context['user'])
    context['worksessionPower'] = brother.hasWorksessionPower()
    getWorkSessions(context, date)
    
    context['worksessions_sat'] = context['worksessions'].filter(date__week_day=7)
    context['worksessions_sun'] = context['worksessions'].filter(date__week_day=1)
    context['weekly_info'] = ''
    
    for d in days:
        if d == 'sat':
            day = 'saturday'
        elif d == 'sun':
            day = 'sunday'

        context[day + '_info'] = "<h5> " + day.capitalize() + " </h5> "
        for worksession in context['worksessions_' + d]:
            button =  """
                      <button class='worksessionDelete'> Delete </button>
                      <button class='worksessionToggle'> %s </button> """ % \
                     ('&#10003' if worksession.completed else 'Make Complete')
            
            if not context['worksessionPower']:
                button = ''

            context[day + '_info'] += """
                <div class='row'>
                    <div class='%s' id='%s'> """ % \
                        (("bg-info" if worksession.completed else "bg-danger"), \
                         str(worksession.id)) 
            context[day + '_info'] += button + """
                        %s
                    </div>
                </div> """ % \
                         str(worksession)

        # If no worksessions exist for this day, display alt-text.
        if (not context['worksessions_' + d]):
            context[day + '_info'] += """
                <div class="row">
                    <h5 class="bg-warning"> No assigned worksession</h5>
                </div>        
                """
        context['weekly_info'] += context[day + '_info']

@login_required
def getUserInfo(request, originalContext):
    context = {}
    context['user'] = request.user
    loadWorksessionWeekHTML(context)

    context['brothers'] = map(lambda ws: ws.displayInfo(), WorksessionBrotherInfo.objects.filter(brother__active=True).order_by('brother__order'));

    if 'newWorksessionForm' not in originalContext:
        context['newWorksessionForm'] = NewWorksessionForm()
    if 'newWorksessionTaskForm' not in originalContext:
        context['newWorksessionTaskForm'] = NewWorksessionTaskForm()
    if 'deleteWorksessionTaskForm' not in originalContext:
        context['deleteWorksessionTaskForm'] = DeleteWorksessionTaskForm()
    if 'newWorkunitForm' not in originalContext:
        context['newWorkunitForm'] = NewWorkunitForm()
    
    return dict(originalContext.items() + context.items())

def getWorkSessions(context, date):
    # date.isocalendar()[2] --> 7 for Sunday. 1 for Monday.
    numericalDayOfWeek = date.isocalendar()[2]
    start = (date + datetime.timedelta(-numericalDayOfWeek)) + datetime.timedelta(6)
    end = start + datetime.timedelta(1)
    context['start_date'] = str(start)
    context['end_date'] = str(end)
    context['worksessions'] = Worksession.objects.filter(date__range=[start, end]).order_by('date')


@login_required
def routeToPage(request, context):
    context = getUserInfo(request, context)
    return render(request, 'ksda/worksessions.html', context)

@login_required
def worksessionsPage(request):
    context = {}
    return routeToPage(request, context)

"""
AJAX Functions
"""
@login_required
@transaction.atomic
def toggleWorksessionComplete(request):
    user = request.user
    if request.method != 'POST' or 'id' not in request.POST:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWorksessionPower():
            return HttpResponse(json.dumps({}), content_type="application/json")
    except Brother.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")

    wsid = request.POST['id']
    worksesh = Worksession.objects.get(id=wsid)
    worksesh.toggleComplete()
    worksesh.save()
    worksesh.brotherinfo.save()
    return HttpResponse(json.dumps({'units':str(worksesh.brotherinfo.units)}), content_type="application/json")       

@login_required
@transaction.atomic
def deleteWorksession(request):
    user = request.user
    if request.method != 'POST' or 'id' not in request.POST:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWorksessionPower():
            return HttpResponse(json.dumps({}), content_type="application/json")
    except Brother.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")
  
    wsid = request.POST['id']
    try:
        worksesh = Worksession.objects.get(id=wsid)
    except Worksession.DoesNotExist:
        # Error case
        return HttpResponse(json.dumps({}), content_type="application/json")       

    if (worksesh.completed):
        worksesh.toggleComplete()
        worksesh.brotherinfo.save()

    units = str(worksesh.brotherinfo.units)

    worksesh.delete()

    return HttpResponse(json.dumps({'units':units}), content_type="application/json")       

@login_required
@transaction.atomic
def deleteWorksessionTask(request):
    context = {}
    user = request.user
    if request.method != 'POST':
        context['dangerMessage'] = 'You can only delete worksession tasks using POST requests.'
        return routeToPage(request, context)
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWorksessionPower():
            context['dangerMessage'] = 'You do not have permission to delete worksession tasks.'
            return routeToPage(request, context)
    except Brother.DoesNotExist:
        return routeToPage(request, context)
  
    form = DeleteWorksessionTaskForm(data=request.POST, username=user.username)

    if not form.is_valid():
        context['dangerMessage'] = 'Invalid worksession task.'
        return routeToPage(request, context)

    wsTask = WorksessionTask.objects.get(name=form.cleaned_data['taskName'])
    wsTask.active = False
    wsTask.save()
    
    context['successMessage'] = 'Worksession task deactivated'
    return routeToPage(request, context)

@login_required
@transaction.atomic
def addWorksessionTask(request):
    context = {}
    user = request.user
    if request.method != 'POST':
        context['dangerMessage'] = 'You can only add worksessions using POST requests.'
        return routeToPage(request, context)
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWorksessionPower():
            context['dangerMessage'] = 'You don\'t have permission to do that.'
            return routeToPage(request, context)
    except Brother.DoesNotExist:
        return routeToPage(request, context)
 
    form = NewWorksessionTaskForm(data=request.POST, username=user.username)
    context['newWorksessionTaskForm'] = form

    if not form.is_valid():
        context['dangerMessage'] = 'Invalid worksession.'
        return routeToPage(request, context)
    
    try:
        ws = WorksessionTask.objects.get(name=form.cleaned_data['taskName'])
        ws.active = True
        ws.save()
    except WorksessionTask.DoesNotExist:
        ws = WorksessionTask.objects.create(name=form.cleaned_data['taskName'])
        ws.save()

    context['successMessage'] = 'Worksession Task Added.'
    return routeToPage(request, context)

@login_required
def getWorksessionInfo(request):
    weekOffset = request.GET['weekOffset']
    date = datetime.date.today() + datetime.timedelta(7 * int(weekOffset))
    context = {}
    context['user'] = request.user
    loadWorksessionWeekHTML(context, date)
    return HttpResponse(json.dumps(\
        {'weekly_info': context['weekly_info'], \
         'start_date' : context['start_date'], \
         'end_date':context['end_date']}) \
         , content_type="application/json") 

@login_required
@transaction.atomic
def addWorksession(request):
    context = {}
    user = request.user

    if request.method != 'POST':
        # Error case
        return routeToPage(request, context)
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWorksessionPower():
            return routeToPage(request, context)
    except Brother.DoesNotExist:
        # Error case
        return routeToPage(request, context)
 

    form = NewWorksessionForm(data=request.POST, username=user.username)
    context['newWorksessionForm'] = form

    if not form.is_valid():
        return routeToPage(request, context)
    task = WorksessionTask.objects.get(name=form.cleaned_data['taskName'])
    ws = Worksession.objects.create(date=form.cleaned_data['date'],
                                    brotherinfo=form.cleaned_data['brother'].worksessionbrotherinfo,
                                    task=task)
    ws.save()

    context['successMessage'] = 'Worksession Added.'
    
    return routeToPage(request, context)

@login_required
@transaction.atomic
def addWorkunit(request):
    context = {}
    user = request.user

    if request.method != 'POST':
        # Error case
        return routeToPage(request, context)
    try:
        brother = Brother.objects.get(user__username=user)
        if not brother.hasWorksessionPower():
            return routeToPage(request, context)
    except Brother.DoesNotExist:
        # Error case
        return routeToPage(request, context)
 

    form = NewWorkunitForm(data=request.POST, username=user.username)
    context['newWorkunitForm'] = form

    if not form.is_valid():
        return routeToPage(request, context)

    brother = Brother.objects.get(id=form.cleaned_data['brother'].id)
    oldUnits = brother.worksessionbrotherinfo.units
    brother.worksessionbrotherinfo.units += form.cleaned_data['newUnits']
    brother.worksessionbrotherinfo.save()
    newUnits = brother.worksessionbrotherinfo.units

    change = 'did not change'
    if oldUnits < newUnits:
        change = 'increased'
    elif oldUnits > newUnits:
        change = 'decreased'

    context['successMessage'] = 'Workunits ' + change + ' for ' + \
                                brother.getName() + ', from ' + \
                                str(oldUnits) + ' to ' + str(newUnits)

    return routeToPage(request, context)

def initializeWorksessions():
    DRB1 = WorksessionTask(name="Dining Room and Bar 1", active=True)
    DRB1.save()
    DRB2 = WorksessionTask(name="Dining Room and Bar 2", active=True)
    DRB2.save()
    DRB3 = WorksessionTask(name="Dining Room and Bar 3", active=True)
    DRB3.save()
    B1 = WorksessionTask(name="Downstairs Bathroom", active=True)
    B1.save()
    B21 = WorksessionTask(name="Second Floor Bathroom 1", active=True)
    B21.save()
    B22 = WorksessionTask(name="Second Floor Bathroom 2", active=True)
    B22.save()
    B31 = WorksessionTask(name="Third Floor Bathroom 1", active=True)
    B31.save()
    B32 = WorksessionTask(name="Third Floor Bathroom 2", active=True)
    B32.save()
    k1 = WorksessionTask(name="Kitchen 1", active=True)
    k1.save()
    k2 = WorksessionTask(name="Kitchen 2", active=True)
    k2.save()
    k3 = WorksessionTask(name="Kitchen 3", active=True)
    k3.save()
    hl = WorksessionTask(name="Halls and Laundry room", active=True)
    hl.save()
    f = WorksessionTask(name="Foyer", active=True)
    f.save()
    ct = WorksessionTask(name="Chapter and TV Room", active=True)
    ct.save()
    k9 = WorksessionTask(name="Sunday Kitchen 9:00pm", active=True)
    k9.save()


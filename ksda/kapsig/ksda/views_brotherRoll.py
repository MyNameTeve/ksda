from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail

from ksda.models import *
from ksda.forms import *

""" 
Routes to appropriate EC page, filling with content along the way.
"""
@login_required
def routeToBrotherRollPage(request, originalContext):
    context = {}
    
    context['user'] = request.user
    brother = Brother.objects.get(user=request.user)
    context['ecPower'] = brother.hasEcPower()

    context['brothers'] = map(lambda b: b.brotherRollInfo(), Brother.objects.filter(active=True).order_by('order'));

    context['pledges'] = map(lambda b: b.pledgeRollInfo(), Brother.objects.filter(pledge=True))

    if 'newRoleForm' not in originalContext:
        context['newRoleForm'] = NewRoleForm()
    
    context['deleteRoleForm'] = DeleteRoleForm()
    context['assignRoleForm'] = AssignRoleForm()

    context = dict(context.items() + originalContext.items())
    
    return render(request, 'ksda/brotherRoll.html', context) 

@login_required
def brotherRoll(request):
    context = {}
    return routeToBrotherRollPage(request, context)

@login_required
@transaction.atomic
def assignRole(request):
    context = {}
    user = request.user
    userBrother = Brother.objects.get(user=request.user)

    if not userBrother.hasEcPower():
        context['dangerMessage'] = 'You are not an EC member -- you cannot assign roles.'
        return routeToBrotherRollPage(request, context)
    
    form = AssignRoleForm(data=request.POST, username=user.username)
    context['assignRoleForm'] = form

    if not form.is_valid():
        context['dangerMessage'] = 'Error Assigning New Role'
        return routeToBrotherRollPage(request, context)
   
    role = Role.objects.get(name=form.cleaned_data['role'])
    brother = Brother.objects.get(user__username=form.cleaned_data['brother'])

    role.brother = brother
    role.save()

    context['successMessage'] = 'Role Assigned'

    return routeToBrotherRollPage(request, context)

@login_required
@transaction.atomic
def newRole(request):
    context = {}
    user = request.user
    userBrother = Brother.objects.get(user=request.user)

    if not userBrother.hasEcPower():
        context['dangerMessage'] = 'You are not an EC member -- you cannot create roles.'
        return routeToBrotherRollPage(request, context)
    
    form = NewRoleForm(data=request.POST, username=user.username)
    context['newRoleForm'] = form

    if not form.is_valid():
        context['dangerMessage'] = 'Error Creating New Role'
        return routeToBrotherRollPage(request, context)
    
    role = Role.objects.create(name=form.cleaned_data['roleName'],
                               finePower=form.cleaned_data['canFine'],
                               worksessionPower=form.cleaned_data['canWorksession'],
                               waitsessionPower=form.cleaned_data['canWaitsession'],
                               ecPower=form.cleaned_data['canEc'])
    role.save()
    context['successMessage'] = 'Role Created'

    return routeToBrotherRollPage(request, context)

@login_required
@transaction.atomic
def deleteRole(request):
    context = {}
    user = request.user
    userBrother = Brother.objects.get(user=request.user)

    if not userBrother.hasEcPower():
        context['dangerMessage'] = 'You are not an EC member -- you cannot delete roles.'
        return routeToBrotherRollPage(request, context)
    
    form = DeleteRoleForm(data=request.POST, username=user.username)

    if not form.is_valid():
        context['dangerMessage'] = 'Error Deleting New Role'
        return routeToBrotherRollPage(request, context)
   
    try:
        role = Role.objects.get(name=form.cleaned_data['roleName'])
    except Role.DoesNotExist:
        context['dangerMessage'] = 'Role Does not Exist'
        return routeToBrotherRollPage(request, context)

    role.delete()
    context['successMessage'] = 'Role Deleted'

    return routeToBrotherRollPage(request, context)

# Initializes all the roles of the system.
def initializeRoles():
    Role.objects.create(name='Grand Master',
                        finePower=True,
                        worksessionPower=True,
                        waitsessionPower=True,
                        ecPower=True)

    Role.objects.create(name='Grand Procurator',
                        finePower=True,
                        worksessionPower=True,
                        waitsessionPower=True,
                        ecPower=True)

    Role.objects.create(name='Grand Master of Ceremonies',
                        finePower=True,
                        worksessionPower=True,
                        waitsessionPower=True,
                        ecPower=True)

    Role.objects.create(name='Grand Scribe',
                        finePower=True,
                        worksessionPower=True,
                        waitsessionPower=True,
                        ecPower=True)

    Role.objects.create(name='Grand Treasurer',
                        finePower=True,
                        worksessionPower=True,
                        waitsessionPower=True,
                        ecPower=True)

    Role.objects.create(name='House Manager',
                        finePower=True,
                        worksessionPower=True,
                        waitsessionPower=True,
                        ecPower=False)

    Role.objects.create(name='Social',
                        finePower=True,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Pledge Educator',
                        finePower=False,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Rush',
                        finePower=True,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Philanthropy',
                        finePower=True,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Alumni Relations',
                        finePower=False,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Scholarship',
                        finePower=True,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Publications',
                        finePower=False,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Design',
                        finePower=False,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Greek Sing Performance',
                        finePower=True,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Greek Sing Philanthropy',
                        finePower=True,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Booth Overall',
                        finePower=True,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Booth Structural',
                        finePower=True,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)    

    Role.objects.create(name='Booth Decorative',
                        finePower=True,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

    Role.objects.create(name='Intramural Sports',
                        finePower=False,
                        worksessionPower=False,
                        waitsessionPower=False,
                        ecPower=False)

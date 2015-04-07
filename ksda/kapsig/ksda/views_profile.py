from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from ksda.models import *
from ksda.forms import *

@login_required
def getUserInfo(request, user, originalContext):
    context = {}
    context['user'] = user
    context['userFirstName'] = user.first_name
    context['userLastName'] = user.last_name
    
    requestingBrother = Brother.objects.get(user=request.user)

    brother = Brother.objects.get(user__username=user)
    
    canEdit = requestingBrother.hasEcPower() or (requestingBrother == brother)
    context['ecPower'] = requestingBrother.hasEcPower()
    
    if 'changePasswordForm' not in originalContext:
        context['changePasswordForm'] = ChangePasswordForm(canEdit=canEdit)
    
    
    if 'updateProfileStandardForm' not in originalContext:
        phoneNumber = brother.number
        email = brother.email
        
        try:
            venmoID = brother.venmoID
        except:
            venmoID = ''

        freeM = brother.waitsessionbrotherinfo.freeM
        freeT = brother.waitsessionbrotherinfo.freeT
        freeW = brother.waitsessionbrotherinfo.freeW
        freeH = brother.waitsessionbrotherinfo.freeH
        freeF = brother.waitsessionbrotherinfo.freeF
        freeThisWeekend = brother.worksessionbrotherinfo.freeThisWeekend
        context['updateProfileStandardForm'] = UpdateProfileStandardForm(canEdit=canEdit,
                                                                         initial={'phoneNumber': phoneNumber,
                                                                                  'email': email,
                                                                                  'venmoID': venmoID,
                                                                                  'freeM': freeM,
                                                                                  'freeT': freeT,
                                                                                  'freeW': freeW,
                                                                                  'freeH': freeH,
                                                                                  'freeF': freeF,
                                                                                  'freeThisWeekend': freeThisWeekend})

    canEdit = requestingBrother.hasEcPower()
    if 'updateProfileAdvancedForm' not in originalContext:
        order = brother.order
        active = brother.active
        pledge = brother.pledge
        context['updateProfileAdvancedForm'] = UpdateProfileAdvancedForm(canEdit=canEdit,
                                                                         initial={'order': order,
                                                                                   'active': active,
                                                                                   'pledge': pledge})

    return dict(originalContext.items() + context.items())

@login_required
def routeToProfile(request, user, context):
    context = getUserInfo(request, user, context)
    return render(request, 'ksda/profile.html', context)

@login_required
def profilePage(request):
    context = {}
    return routeToProfile(request, request.user, context)

@login_required
def profilePageObserved(request, observedUserName):
    user = User.objects.get(username=observedUserName)
    context = {}
    return routeToProfile(request, user, context)


@login_required
@transaction.atomic
def updateProfileStandard(request):
    context = {}

    if request.method != 'POST' or 'observedUser' not in request.POST:
        context['dangerMessage'] = 'Only accepting post methods with this request.'
        return routeToProfile(request, request.user, context)
    observedUserName = request.POST['observedUser']
    observedUser = User.objects.get(username=observedUserName)

    requestingBrother = Brother.objects.get(user=request.user)
    brother = Brother.objects.get(user__username=observedUser)

    if not brother:
        context['dangerMessage'] = 'You cannot edit this brother -- they do not exist'
        return routeToProfile(request, observedUser, context)

    canEdit = requestingBrother.hasEcPower() or (requestingBrother == brother)
    
    if not canEdit:
        context['dangerMessage'] = 'You cannot edit this profile'
        return routeToProfile(request, observedUser, context)

    form = UpdateProfileStandardForm(data=request.POST, canEdit=canEdit)
    context['updateProfileStandardForm'] = form
    if not form.is_valid():
        context['dangerMessage'] = 'Did not update profile'
        return routeToProfile(request, observedUser, context)
    
    brother.number = form.cleaned_data['phoneNumber']
    brother.email = form.cleaned_data['email']
    brother.venmoID = form.cleaned_data['venmoID']
    brother.waitsessionbrotherinfo.freeM = form.cleaned_data['freeM']
    brother.waitsessionbrotherinfo.freeT = form.cleaned_data['freeT']
    brother.waitsessionbrotherinfo.freeW = form.cleaned_data['freeW']
    brother.waitsessionbrotherinfo.freeH = form.cleaned_data['freeH']
    brother.waitsessionbrotherinfo.freeF = form.cleaned_data['freeF']
    brother.worksessionbrotherinfo.freeThisWeekend = form.cleaned_data['freeThisWeekend']

    brother.save()
    brother.waitsessionbrotherinfo.save()
    brother.worksessionbrotherinfo.save()
    
    context['successMessage'] = 'Profile Updated'
    return routeToProfile(request, observedUser, context)

@login_required
@transaction.atomic
def updateProfileAdvanced(request):
    context = {}

    if request.method != 'POST' or 'observedUser' not in request.POST:
        context['dangerMessage'] = 'Only accepting post methods with this request.'
        return routeToProfile(request, request.user, context)
    observedUserName = request.POST['observedUser']
    observedUser = User.objects.get(username=observedUserName)

    try:
        requestingBrother = Brother.objects.get(user=request.user)
        brother = Brother.objects.get(user__username=observedUser)
    except:
        context['dangerMessage'] = 'You cannot edit this brother -- they do not exist'
        return routeToProfile(request, observedUser, context)

    canEdit = requestingBrother.hasEcPower()
    
    if not canEdit:
        context['dangerMessage'] = 'You need EC access to edit this information'
        return routeToProfile(request, observedUser, context)

    form = UpdateProfileAdvancedForm(data=request.POST, canEdit=canEdit)
    context['updateProfileAdvancedForm'] = form
    if not form.is_valid():
        context['dangerMessage'] = 'Did not update profile'
        return routeToProfile(request, observedUser, context)
    
    brother.order = form.cleaned_data['order']
    brother.active = form.cleaned_data['active']
    brother.pledge = form.cleaned_data['pledge']

    brother.save()
    
    context['successMessage'] = 'Profile Updated'
    return routeToProfile(request, observedUser, context)

@login_required
@transaction.atomic
def changePassword(request):
    context = {}
    if request.method != 'POST' or 'observedUser' not in request.POST:
        context['dangerMessage'] = 'Only accepting post methods with this request.'
        return routeToProfile(request, request.user, context)

    observedUserName = request.POST['observedUser']
    observedUser = User.objects.get(username=observedUserName)
    
    requestingBrother = Brother.objects.get(user=request.user)
    brother = Brother.objects.get(user__username=observedUserName)

    if not brother:
        context['dangerMessage'] = 'You cannot edit this brother -- they do not exist'
        return routeToProfile(request, observedUser, context)

    canEdit = requestingBrother.hasEcPower() or (requestingBrother == brother)
    
    if not canEdit:
        context['dangerMessage'] = 'You cannot edit this profile'
        return routeToProfile(request, observedUser, context)

    form = ChangePasswordForm(data=request.POST, canEdit=canEdit)
    context['changePasswordForm'] = form

    if not form.is_valid():
        return routeToProfile(request, observedUser, context)
    
    observedUser.set_password(form.cleaned_data['password1'])
    observedUser.save()

    context['successMessage'] = 'Password Changed.'
    return routeToProfile(request, observedUser, context)


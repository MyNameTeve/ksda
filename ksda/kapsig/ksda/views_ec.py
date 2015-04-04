from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail

from ksda.models import *
from ksda.forms import *

@login_required
def isEcMember(request):
    user = request.user
    brother = Brother.objects.get(user=user)
    return brother.hasEcPower()

""" 
Routes to appropriate EC page, filling with content along the way.
"""
@login_required
def routeToEcPage(request, originalContext):
    context = {}
    
    context['ecMembership'] = True
    context['user'] = request.user
    if 'sendEmailForm' not in originalContext:
        context['sendEmailForm'] = SendEmailForm()

    context = dict(context.items() + originalContext.items())
    
    return render(request, 'ksda/ec.html', context) 

@login_required
def ecPage(request):
    context = {}
    if isEcMember(request):
        context['successMessage'] = 'Welcome, EC member!'
        return routeToEcPage(request, context)
    else:
        context['dangerMessage'] = 'Unfortunately, you are not on the EC.'
        return render(request, 'ksda/ec.html', context) 

@login_required
@transaction.atomic
def sendEmail(request):
    context = {}
    
    user = request.user
    form = SendEmailForm(data=request.POST, username=user.username)
    context['sendEmailForm'] = form

    if not form.is_valid():
        return routeToEcPage(request, context)


    send_mail(form.cleaned_data['email_title'], 
              form.cleaned_data['email_content'], 
              'from@example.com',
              ['to@example.com'], 
              fail_silently=False)
    
    context['successMessage'] = 'Email sent.'
    return routeToEcPage(request, context)

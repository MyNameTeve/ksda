from django.shortcuts import render, redirect

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from ksda.models import *
from ksda.forms import *

from django.core.mail import send_mail

@login_required
def forumPage(request):
    threads = Thread.objects.all().order_by('-updated')
    user_profile = Brother.objects.get(user=request.user)
    return render(request, 'ksda/forum.html', {'threads': threads, 'threadform': ThreadForm()})

@login_required
@transaction.atomic
def new_thread(request):
    errors = []
    context = {}
    threads = Thread.objects.all().order_by('-updated')
    if request.method == 'GET':
        context['threadform'] = ThreadForm()
        context['threads'] = items
        context['errors'] = errors
        return render(request, 'ksda/forum.html', context)

    threadform = ThreadForm(request.POST)
    context['threadform'] = threadform

    if not threadform.is_valid():
        errors.append('You must enter an item to add.')
        context['threadform'] = ThreadForm()
        context['threads'] = threads
        context['errors'] = errors
        return render(request, 'ksda/forum.html', context)

    brother = Brother.objects.get(user=request.user)

    tid = TID.objects.get()
    ID = tid.currentID
    new_thread = Thread(title=threadform.cleaned_data['Title'],
                        content=threadform.cleaned_data['Content'],
                        brother = brother,
                        threadID = tid.currentID)
    new_thread.save()
    tid.currentID = tid.currentID + 1
    tid.save()
    threads = Thread.objects.all().order_by('-updated')
    context['threadform'] = ThreadForm()
    context['threads'] = threads
    context['errors'] = errors
    context['successMessage'] = 'Created new thread.'

    #Send out an email to the brotherhood for a new forum post
    brothers = Brother.objects.all().filter(active=True)
    emails=[]
    for b in brothers:
        emails.append(b.email)

    email_body = """
    
            %s %s, has created a new forum post. \n
            Title:  %s \n
            %s 
        """ % (request.user.first_name,
               request.user.last_name,
               threadform.cleaned_data['Title'],
               threadform.cleaned_data['Content'])

       
        
    
    #send the email to everyone
    send_mail(subject="New Post to the KSDA Forum",
                message=email_body,
                from_email="kappasigmadeltaalpha@gmail.com",
                recipient_list=emails)

    return render(request, 'ksda/forum.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseRedirect

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.core import serializers

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from ksda.models import *

from ksda.forms import *
from django.utils import timezone

from django.core.mail import send_mail

from django.contrib.auth.tokens import default_token_generator

#from socialnetwork.s3 import s3_upload, s3_delete

@login_required
def forumPage(request):
    # Sets up list of just the logged-in user's (request.user's) items
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
        return render(request, 'ksda/threads.html', context)

    threadform = ThreadForm(request.POST)
    context['threadform'] = threadform

    if not threadform.is_valid():
        errors.append('You must enter an item to add.')
        context['threadform'] = ThreadForm()
        context['threads'] = threads
        context['errors'] = errors
        return render(request, 'ksda/threads.html', context)

    # Just display the registration form if this is a GET request

    brother = Brother.objects.get(user=request.user)

    tid = TID.objects.get()
    ID = tid.currentID
    new_thread = Thread(title=threadform.cleaned_data['Title'],content=threadform.cleaned_data['Content'], brother = brother, threadID = tid.currentID)
    new_thread.save()
    tid.currentID = tid.currentID + 1
    tid.save()
    #user_profile.most_recent_update = timezone.now()
    #brother.save()
    threads = Thread.objects.all().order_by('-updated')
    context['threadform'] = ThreadForm()
    context['threads'] = threads
    context['errors'] = errors
    return render(request, 'ksda/forum.html', context)


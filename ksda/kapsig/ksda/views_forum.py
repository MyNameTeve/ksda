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




############################## HOME ##############################
##############################          ##############################

@login_required
def forum(request):
    # Sets up list of just the logged-in user's (request.user's) items
    items = Item.objects.all().order_by('-dateTime')
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.most_recent_update = timezone.now()
    user_profile.save()
    return render(request, 'ksda/forum.html', {'items' : items, 'user_profile' : user_profile, 'postform': PostForm()})




############################


@login_required
@transaction.atomic
def post(request):
    errors = []
    context = {}
    items = Item.objects.all().order_by('-dateTime')
    if request.method == 'GET':
        context['postform'] = PostForm()
        context['items'] = items
        context['errors'] = errors
        return render(request, 'ksda/forum.html', context)

    postform = PostForm(request.POST)
    context['postform'] = postform

    if not postform.is_valid():
        errors.append('You must enter an item to add.')
        context['postform'] = PostForm()
        context['items'] = items
        context['errors'] = errors
        return render(request, 'ksda/forum.html', context)

    # Just display the registration form if this is a GET request

    user_profile = UserProfile.objects.get(user=request.user)

    
    new_item = Item(text=postform.cleaned_data['Post'], user=request.user, user_profile = user_profile, dateTime = timezone.now())
    new_item.save()
    user_profile.most_recent_update = timezone.now()
    user_profile.save()
    items = Item.objects.all().order_by('-dateTime')
    context['postform'] = PostForm()
    context['items'] = items
    context['errors'] = errors
    return render(request, 'ksda/forum.html', context)


############################## REGISTER ##############################
##############################          ##############################



@login_required
def get_stream_json(request):
    user_profile = UserProfile.objects.get(user = request.user)
    context = {'items': Item.objects.filter(dateTime__gte = user_profile.most_recent_update).order_by('-dateTime') }
    user_profile.most_recent_update = timezone.now()
    user_profile.save()
    return render(request, "ksda/stream.html", context)

@login_required
@transaction.atomic
def get_comment_html(request):
    context = {}
    if not 'text' in request.GET or not request.GET['text']:
        console.log("error no comment")
    else:
        user_profile = UserProfile.objects.get(user = request.user)
        new_comment = Comment(text= request.GET['text'] , user=request.user, user_profile = user_profile, dateTime = timezone.now())
        new_comment.save()
        target_post = Item.objects.get(id=request.GET['id'])
        target_post.comments.add(new_comment)
        target_post.save()
        context =  {'comment': new_comment}

    return render(request, 'ksda/comment.html', context)

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




############################## Main Thread screen ##############################
##############################          ##############################

@login_required
def threads(request, id):
    #determines the thread id you are looking at and gets the thread object
    thread = Thread.objects.get(threadID = id)
    brother = thread.brother

    #items are the responses to that thread
    items = thread.responses.all
    user_profile = Brother.objects.get(user=request.user)
    return render(request, 'ksda/thread.html', {'items' : items, 'user_profile' : user_profile, 'postform': PostForm(), 'title': thread.title,'brother': brother, 'content': thread.content, 'thread': thread})




############################   New Response  ############################

#Creates a new  repsonse in the thread
@login_required
@transaction.atomic
def post(request, id):
    errors = []
    context = {}
    thread = Thread.objects.get(threadID = id)
    items = thread.responses.all
    user_profile = Brother.objects.get(user=request.user)
    print thread.brother.user
    brother = thread.brother

    #if you are just getting then return the original information
    if request.method == 'GET':
        context['postform'] = PostForm()
        context['items'] = items
        context['errors'] = errors
        context['brother'] = brother
        context['thread'] = thread
        context['user_profile'] = user_profile
        context['title'] = thread.title
        context['content'] = thread.content
        return render(request, 'ksda/thread.html', context)

    postform = PostForm(request.POST)
    context['postform'] = postform

    #if the input to the form is not valid then return back to the original form
    if not postform.is_valid():
        errors.append('You must enter an item to add.')
        context['postform'] = PostForm()
        context['items'] = items
        context['errors'] = errors
        context['thread'] = thread
        context['brother'] = brother
        context['user_profile'] = user_profile
        context['title'] = thread.title
        context['content'] = thread.content 
        return render(request, 'ksda/thread.html', context)

    #otherwise create a new item to be posted and added to items

    user_profile = Brother.objects.get(user=request.user)
    brother = thread.brother

    
    new_item = Item(text=postform.cleaned_data['Post'], brother = user_profile, dateTime = timezone.now())
    new_item.save()
    user_profile.save()
    items = thread.responses.all
    context['postform'] = PostForm()
    context['items'] = items
    context['errors'] = errors
    context['thread'] = thread
    context['brother'] = brother
    context['user_profile'] = user_profile
    context['title'] = thread.title
    context['content'] = thread.content

    #add the new item into the list of items in the thread object
    thread.responses.add(new_item)
    thread.save()
    return render(request, 'ksda/thread.html', context)




#code for generating a comment
@login_required
@transaction.atomic
def get_comment_html(request):
    context = {}
    if not 'text' in request.GET or not request.GET['text']:
        console.log("error no comment")
    else:
        user_profile = Brother.objects.get(user = request.user)
        new_comment = Comment(text= request.GET['text'] , brother = user_profile, dateTime = timezone.now())
        new_comment.save()
        target_post = Item.objects.get(id=request.GET['id'])
        target_post.comments.add(new_comment)
        target_post.save()
        context =  {'comment': new_comment}

    return render(request, 'ksda/comment.html', context)

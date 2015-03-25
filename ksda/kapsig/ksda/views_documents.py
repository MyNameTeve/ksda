from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from ksda.models import *
from ksda.forms import *
from ksda.s3 import *

"""
Routes to Documents page, filling with content along the way.
"""
@login_required
def routeToDocumentsPage(request, originalContext):
    context = {}

    context['user'] = request.user
    brother = Brother.objects.get(user=request.user)
    context['ecPower'] = brother.hasEcPower()

    if 'form' not in originalContext:
        context['form'] = UploadForm()

    # Add code to add documents to table
    context['documents'] = Document.objects.all().values('user')
    print len(context['documents'])

    context = dict(context.items() + originalContext.items())

    # Just display the upload form and document table if this is a GET request
    if request.method == 'GET':
        return render(request, 'ksda/documents.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary
    form = UploadForm(request.POST, request.FILES)
    context['form'] = form

    # Validate the form
    if not form.is_valid():
        return render(request, 'ksda/documents.html', context)

    new_document = Document(user=request.user,
                            title='Hello',
                            file='')

    if form.cleaned_data['file'] is not None:
        url = s3_upload(form.cleaned_data['file'], request.user.id)
        new_document.file = url

    new_document.save()

    return render(request, 'ksda/documents.html', context)

@login_required
def documentsPage(request):
    context = {}
    return routeToDocumentsPage(request, context)
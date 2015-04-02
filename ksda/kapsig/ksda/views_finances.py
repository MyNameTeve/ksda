from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required
def routeToFinancesPage(request, originalContext):
    context = {}
    context = dict(context.items() + originalContext.items())
    return render(request, 'ksda/finances.html', context)

@login_required
def financesPage(request):
    context = {}
    return routeToFinancesPage(request, context)
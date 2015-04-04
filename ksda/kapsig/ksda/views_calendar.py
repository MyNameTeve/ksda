from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def calendarPage(request):
    context = {}
    return render(request, 'ksda/calendar.html', context)
from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.forms.extras.widgets import SelectDateWidget
from django.db import models

from datetimewidget.widgets import DateWidget

from ksda.models import *

import datetime

class UserModelChoiceField(forms.ModelChoiceField):
    # Helper Field to select from brothers.
    # TODO: Move to forms.py
    def label_from_instance(self, obj):
        return '[' + str(obj.waitsessionbrotherinfo.units) + '] ' + obj.user.first_name + \
                ' ' + obj.user.last_name + ' (' + obj.user.username + ')'

class NewWaitsessionForm(forms.Form):
    # Fun little widget used here, from https://github.com/asaglimbeni/django-datetime-widget 
    # Weekends are disabled for waitsessions.
    date = forms.DateField(widget=DateWidget(usel10n=True,
                                             bootstrap_version=3,
                                             options={
                                                     'daysOfWeekDisabled':'[0,6]'
                                                     }))
    
    brother = UserModelChoiceField(label='Brother Assigned',
                                queryset=Brother.objects.filter(active=True).order_by('waitsessionbrotherinfo__units'))
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(NewWaitsessionForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewWaitsessionForm, self).clean()

        date = cleaned_data.get('date')
        brother = cleaned_data.get('brother')
        
        if not date:
            raise forms.ValidationError('Date is required')
        if not brother in Brother.objects.filter(active=True):
            raise forms.ValidationError('Brother is not active')
        if Waitsession.objects.filter(date=cleaned_data['date'],
                                      brotherinfo=cleaned_data['brother'].waitsessionbrotherinfo).exists():
            raise forms.ValidationError('Brother already has a waitsession at this time')

        return cleaned_data

class NewWaitunitForm(forms.Form):
    newUnits = forms.DecimalField(label='Change in Units', decimal_places=0)

    brother = UserModelChoiceField(label='Brother Assigned',
                                queryset=Brother.objects.filter(active=True).order_by('order'))

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(NewWaitunitForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewWaitunitForm, self).clean()

        newUnits = cleaned_data.get('newUnits')
        brother = cleaned_data.get('brother')

        if not brother in Brother.objects.filter(active=True):
            raise forms.ValidationError('Brother is not active')

        return cleaned_data



from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.forms.extras.widgets import SelectDateWidget
from django.db import models

from datetimewidget.widgets import DateWidget

from ksda.models import *

import datetime

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '[' + str(obj.worksessionbrotherinfo.units) + '] ' + obj.user.first_name + \
                ' ' + obj.user.last_name + ' (' + obj.user.username + ')'

class NewWorksessionForm(forms.Form):
    # Fun little widget used here, from https://github.com/asaglimbeni/django-datetime-widget 
    date = forms.DateField(widget=DateWidget(usel10n=True,
                                             bootstrap_version=3,
                                             options={
                                                     'daysOfWeekDisabled':'[1,2,3,4,5]'
                                                     }))
    
    brother = UserModelChoiceField(label='Brother Assigned',
                                queryset=Brother.objects.filter(active=True).order_by('worksessionbrotherinfo__units'))
    taskName = forms.ChoiceField()
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(NewWorksessionForm, self).__init__(*args, **kwargs)
        self.fields['taskName'] = forms.ChoiceField(label='Task Name', choices=[(task, task.name) for task in WorksessionTask.objects.filter(active=True)])

    def clean(self):
        cleaned_data = super(NewWorksessionForm, self).clean()

        date = cleaned_data.get('date')
        brother = cleaned_data.get('brother')
        
        if not date:
            raise forms.ValidationError('Date is required')
        elif not brother in Brother.objects.filter(active=True):
            raise forms.ValidationError('Brother is not active')
        elif Worksession.objects.filter(date=cleaned_data['date'],
                                      brotherinfo=cleaned_data['brother'].worksessionbrotherinfo).exists():
            raise forms.ValidationError('Brother already has a worksession at this time')
        elif not WorksessionTask.objects.filter(active=True).filter(name=cleaned_data['taskName']).exists():
            raise forms.ValidationError('Task does not exist')
        elif Worksession.objects.filter(date=date).filter(task=WorksessionTask.objects.get(name=cleaned_data['taskName'])).exists():
            raise forms.ValidationError('Task already assigned to someone.')

        return cleaned_data

class NewWorksessionTaskForm(forms.Form):
    taskName = forms.CharField(label='New Task Name')
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(NewWorksessionTaskForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super(NewWorksessionTaskForm, self).clean()
        name = cleaned_data.get('taskName')
        if WorksessionTask.objects.filter(name=name).filter(active=True).exists():
            raise forms.ValidationError('Task already exists')
        
        return cleaned_data

class DeleteWorksessionTaskForm(forms.Form):
    taskName = forms.ChoiceField()
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(DeleteWorksessionTaskForm, self).__init__(*args, **kwargs)
        self.fields['taskName'] = forms.ChoiceField(label='Task Name', choices=[(task, task.name) for task in WorksessionTask.objects.filter(active=True).order_by('name')])
     
    def clean(self):
        cleaned_data = super(DeleteWorksessionTaskForm, self).clean()
        name = cleaned_data.get('taskName')
        if not WorksessionTask.objects.filter(name=name).filter(active=True).exists():
            raise forms.ValidationError('Task does not exist')
        return cleaned_data

class NewWorkunitForm(forms.Form):
    newUnits = forms.DecimalField(label='Change in Units', decimal_places=0)
    brother = UserModelChoiceField(label='Brother Assigned',
                                queryset=Brother.objects.filter(active=True).order_by('order'))

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(NewWorkunitForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewWorkunitForm, self).clean()

        newUnits = cleaned_data.get('newUnits')
        brother = cleaned_data.get('brother')

        if not brother in Brother.objects.filter(active=True):
            raise forms.ValidationError('Brother is not active')

        return cleaned_data



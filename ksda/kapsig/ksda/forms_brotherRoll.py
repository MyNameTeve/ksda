from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import models

from ksda.models import *

class UserModelChoiceField(forms.ModelChoiceField):
    # Helper Field to select from brothers.
    def label_from_instance(self, obj):
        return '[' + str(obj.order) + '] ' + obj.user.first_name + \
                ' ' + obj.user.last_name + ' (' + obj.user.username + ')'

class NewRoleForm(forms.Form):
    roleName = forms.CharField(label='Role Name')
    canFine = forms.BooleanField(label='Fining Power',required=False)
    canWorksession = forms.BooleanField(label='Can edit worksessions',required=False)
    canWaitsession = forms.BooleanField(label='Can edit waitsessions',required=False)
    canEc = forms.BooleanField(label='Has EC privileges',required=False)
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(NewRoleForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewRoleForm, self).clean()

        roleName = cleaned_data.get('roleName')
       
        if Role.objects.filter(name=roleName).exists():
            raise forms.ValidationError('Role already exists')

        return cleaned_data

class DeleteRoleForm(forms.Form):
    roleName = forms.ChoiceField()
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(DeleteRoleForm, self).__init__(*args, **kwargs)
        self.fields['roleName'] = forms.ChoiceField(label='Role Name', choices=[(role, role.name) for role in Role.objects.all()])

    def clean(self):
        cleaned_data = super(DeleteRoleForm, self).clean()
        
        roleName = cleaned_data.get('roleName')
        if Role.objects.filter(name=roleName).exists():
            return cleaned_data
        else:
            raise forms.ValidationError('Role does not exist')

class AssignRoleForm(forms.Form):
    role = forms.ChoiceField(choices=[(role, role) for role in Role.objects.all()])

    brother = UserModelChoiceField(label='Brother Assigned',
                                queryset=Brother.objects.filter(active=True).order_by('order'))

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(AssignRoleForm, self).__init__(*args, **kwargs)
        self.fields['role'] = forms.ChoiceField(choices=[(role, role) for role in Role.objects.all()])
        self.fields['brother'] = UserModelChoiceField(label='Brother Assigned',
                                                      queryset=Brother.objects.filter(active=True).order_by('order'))

    def clean(self):
        cleaned_data = super(AssignRoleForm, self).clean()
       
        try:
            role = Role.objects.get(name=cleaned_data.get('role'))
            brother = Brother.objects.get(user__username=cleaned_data.get('brother'))
        except:
            raise forms.ValidationError('Missing role or brother')

        return cleaned_data


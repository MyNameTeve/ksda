from django import forms
from django.contrib.auth.models import User
from django.db import models
from ksda.models import *

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '[' + str(obj.worksessionbrotherinfo.units) + '] ' + obj.user.first_name + \
            ' ' + obj.user.last_name + ' (' + obj.user.username + ')'

class RoleModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.name)

class NewFineForm(forms.Form):
    chair = RoleModelChoiceField(label='Chair',
                                 queryset=Role.objects.all())
    brother = UserModelChoiceField(label='Finee',
                                   queryset=Brother.objects.filter(active=True))
    amount = forms.DecimalField(label='Fine Amount',
                                max_digits=5,
                                decimal_places=2)
    reason = forms.CharField(label='Reason')

    def clean(self):
        cleaned_data = super(NewFineForm, self).clean()

        amount = self.cleaned_data.get('amount')
        reason = self.cleaned_data.get('reason')
        brother = self.cleaned_data.get('brother')
        chair = self.cleaned_data.get('chair')
        
        if not amount:
            raise forms.ValidationError('Fine amount is required.')
        elif not reason:
            raise forms.ValidationError('Reason is required.')
        elif not brother in Brother.objects.filter(active=True):
            raise forms.ValidationError('Finee is required.')
        elif not chair:
            raise forms.ValidationError('Chair is required.')
        return cleaned_data
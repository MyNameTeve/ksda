from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class SendEmailForm(forms.Form):
    email_title = forms.CharField(max_length = 1000,
                                  label='Email Title',
                                  widget = forms.TextInput())

    email_content = forms.CharField(max_length = 5000,
                                  label='Email Content',
                                  widget = forms.Textarea())
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(SendEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SendEmailForm, self).clean()

        title = cleaned_data.get('email_title')
        content = cleaned_data.get('email_content')

        if title == '' or title == None:
            raise forms.ValidationError('Title needed to send email') 
        if content == '' or content == None:
            raise forms.ValidationError('Content needed to send email')

        return cleaned_data


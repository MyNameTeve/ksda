from django import forms

from django.contrib.auth.models import User

# Importing all forms from submodules within the site.
from forms_profile import *
from forms_ec import *
from forms_waitsession import *
from forms_worksession import *
from forms_brotherRoll import *

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length = 30)
    last_name = forms.CharField(max_length = 30)
    username = forms.CharField(max_length = 20)
    password1 = forms.CharField(max_length = 200,
                                label='Password',
                                widget = forms.PasswordInput())
    password2 = forms.CharField(max_length = 200,
                                label='Confirm Password',
                                widget = forms.PasswordInput())\

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords did not match.')

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError('Username is already taken.')

        return username

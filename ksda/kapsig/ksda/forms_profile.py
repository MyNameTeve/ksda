from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from phonenumber_field.modelfields import PhoneNumberField

class ChangePasswordForm(forms.Form):
    """
    oldpassword = forms.CharField(max_length = 200,
                                  label='Old Password',
                                  widget = forms.PasswordInput())
    """

    password1 = forms.CharField(max_length = 200,
                                  label='New Password',
                                  widget = forms.PasswordInput())

    password2 = forms.CharField(max_length = 200,
                                  label='Confirm new Password',
                                  widget = forms.PasswordInput())
    
    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        self.canEdit = kwargs.pop('canEdit', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        if not self.canEdit:
            for f in self.fields.items():
                f[1].widget.attrs['readonly'] = True
            

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('New passwords did not match.')
        """
        user = authenticate(username=self.username, password=cleaned_data.get('oldpassword'))
        if user is not None:
            print 'valid old password'
        else:
            print 'old password invalid'
            raise forms.ValidationError('Old password invalid.')
        """
        return cleaned_data

class UpdateProfileStandardForm(forms.Form):
    email = forms.EmailField()
    phoneNumber = forms.CharField(label="Phone Number")
    venmoID = forms.CharField(label='Venmo ID', required=False)
    freeM = forms.BooleanField(label="Free for Waitsession on Monday", required=False)
    freeT = forms.BooleanField(label="Free for Waitsession on Tuesday", required=False)
    freeW = forms.BooleanField(label="Free for Waitsession on Wednesday", required=False)
    freeH = forms.BooleanField(label="Free for Waitsession on Thursday", required=False)
    freeF = forms.BooleanField(label="Free for Waitsession on Friday", required=False)
    freeThisWeekend = forms.BooleanField(label="Free for Worksession this Weekend", required=False)

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        self.canEdit = kwargs.pop('canEdit', None)
        super(UpdateProfileStandardForm, self).__init__(*args, **kwargs)
        if not self.canEdit:
            for f in self.fields.items():
                f[1].widget.attrs['readonly'] = 'True'
                f[1].widget.attrs['disabled'] = 'True'

    def clean(self):
        cleaned_data = super(UpdateProfileStandardForm, self).clean()

        number = cleaned_data.get('phoneNumber')
        if not number:
            raise forms.ValidationError("Invalid phone number. Please enter in the format 555-555-5555.")

        numArray = number.split('-')
        if not (len(numArray) == 3 and 
                len(numArray[0]) == 3 and 
                len(numArray[1]) == 3 and 
                len(numArray[2]) == 4 and 
                numArray[0].isdigit() and
                numArray[1].isdigit() and
                numArray[2].isdigit()):
            raise forms.ValidationError("Invalid phone number. Please enter in the format 555-555-5555.")

        return cleaned_data

class UpdateProfileAdvancedForm(forms.Form):
    order = forms.DecimalField()
    active = forms.BooleanField(required=False)
    pledge = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        self.canEdit = kwargs.pop('canEdit', None)
        super(UpdateProfileAdvancedForm, self).__init__(*args, **kwargs)
        if not self.canEdit:
            for f in self.fields.items():
                f[1].widget.attrs['readonly'] = 'True'
                f[1].widget.attrs['disabled'] = 'True'

    def clean(self):
        cleaned_data = super(UpdateProfileAdvancedForm, self).clean()
       
        order = cleaned_data.get('order')
        if order < 0:
            raise forms.ValidationError("Positive order only")

        return cleaned_data

from django import forms


class PostForm(forms.Form):
    Post = forms.CharField(max_length=160, required=False)


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(PostForm, self).clean()

class ThreadForm(forms.Form):
    Title = forms.CharField(max_length=100, required=False)
    Content = forms.CharField(max_length=1000, required=False)

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(ThreadForm, self).clean()
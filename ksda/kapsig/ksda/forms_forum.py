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
    Content = forms.CharField(max_length=1000, required=False, widget=forms.Textarea)

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(ThreadForm, self).clean()

    def clean_Content(self):
        content = self.cleaned_data['Content']
        if not content:
            raise forms.ValidationError('Please add content to your post')
        return content

    def clean_Title(self):
        title = self.cleaned_data['Title']
        if not title:
            raise forms.ValidationError('Please add a title to your post')
        return title

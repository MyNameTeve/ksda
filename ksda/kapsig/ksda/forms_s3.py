from django import forms

#MAX_UPLOAD_SIZE = 2500000

class UploadForm(forms.Form):
    file = forms.FileField(label='Document')

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(UploadForm, self).clean()
        
        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the file field.
    def clean_file(self):
        file = self.cleaned_data['file']
        if not file:
            return None
        if not file.content_type:
            raise forms.ValidationError('File type is not existent')
            #if file.size > MAX_UPLOAD_SIZE:
            #raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return file
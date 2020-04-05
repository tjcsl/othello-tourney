from django import forms


class UploadFileForm(forms.Form):
    code = forms.FileField()

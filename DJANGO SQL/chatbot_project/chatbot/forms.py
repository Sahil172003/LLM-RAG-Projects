from django import forms
from .models import UploadedFile

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']

class QueryForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ask questions about your SQL file'}))
from django import forms

from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('code', )


class GameForm(forms.Form):
    choices = Submission.objects.order_by('user', '-submitted_time').distinct('user')
    black = forms.ModelChoiceField(label="Black:", queryset=choices, initial="Yourself")
    white = forms.ModelChoiceField(label="White:", queryset=choices, initial="Yourself")
    time_limit = forms.IntegerField(label="Time Limit (secs):", initial=5, min_value=1)

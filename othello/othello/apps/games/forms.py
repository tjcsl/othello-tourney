from django import forms

from .models import Submission, Game


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('code', )


class GameForm(forms.Form):
    choices = [(submission.id, submission.user) for submission in Submission.objects.order_by('user', '-submitted_time').distinct('user')]
    black = forms.ChoiceField(label="Black:", choices=choices, initial="Yourself")
    white = forms.ChoiceField(label="White:", choices=choices, initial="Yourself")
    time_limit = forms.IntegerField(label="Time Limit (secs):", initial=5, min_value=1)

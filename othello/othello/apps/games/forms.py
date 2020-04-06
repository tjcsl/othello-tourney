from django import forms

from .models import Submission, Game


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('code', )


class GameForm(forms.Form):
    choices = Submission.objects.order_by('user', '-submitted_time').distinct('user')
    black = forms.ModelChoiceField(queryset=choices, empty_label="Player 1")
    white = forms.ModelChoiceField(queryset=choices, empty_label="Player 2")
    time_limit = forms.IntegerField(initial=5, min_value=1)

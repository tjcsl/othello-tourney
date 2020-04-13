from django import forms

from ..models import Game, Submission


class GameForm(forms.Form):
    choices = Submission.objects.all_usable_submissions()
    black = forms.ModelChoiceField(label="Black:", queryset=choices, initial="Yourself")
    white = forms.ModelChoiceField(label="White:", queryset=choices, initial="Yourself")
    time_limit = forms.IntegerField(label="Time Limit (secs):", initial=5, min_value=1)


class WatchForm(forms.Form):
    games = forms.ModelChoiceField(label="Running Games:", queryset=Game.objects.get_all_running())

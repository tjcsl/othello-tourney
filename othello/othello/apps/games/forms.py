from django import forms

from .models import Submission, Game


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('code', )


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('black', 'white', 'time_limit')
        widgets = {
            'black': forms.Select(attrs={'placeholder': 'Player 1'}),
            'white': forms.Select(attrs={'placeholder': 'Player 2'}),
        }

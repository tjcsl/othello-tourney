from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import Tournament


class TournamentForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        label="Start Time: ",
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def clean(self):
        cd = self.cleaned_data
        if not cd["include_users"].exists():
            raise ValidationError("Cannot run a tournament with all users excluded!")
        if cd["include_users"].filter(username="Yourself").exists():
            raise ValidationError("The \"Yourself\" player cannot participate in Tournaments!")

    class Meta:
        model = Tournament
        exclude = ('finished',)
        labels = {
            "include_users": "Include Users: "
        }

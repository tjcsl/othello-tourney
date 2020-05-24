from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
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
        if not cd["exclude_users"].difference(get_user_model().objects.all()).exists():
            raise ValidationError("Cannot run a tournament with all users excluded!")

    class Meta:
        model = Tournament
        exclude = ('finished',)
        labels = {
            "exclude_users": "Exclude Users: "
        }

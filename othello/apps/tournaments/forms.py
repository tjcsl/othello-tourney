from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import Tournament


class TournamentCreateForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        label="Start Time: ",
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    game_time_limit = forms.IntegerField(label="Game Time Limit: ", min_value=1, max_value=15,)

    def clean(self):
        cd = self.cleaned_data
        if cd["include_users"].count() >= 2:
            raise ValidationError("A Tournament must include at least 2 players!")
        if (
            cd["include_users"].filter(username="Yourself").exists()
            or cd["bye_player"].username == "Yourself"
        ):
            raise ValidationError('The "Yourself" player cannot participate in Tournaments!')

    class Meta:
        model = Tournament
        exclude = ("finished",)
        labels = {"include_users": "Include Users: ", "bye_player": "Bye Player: "}

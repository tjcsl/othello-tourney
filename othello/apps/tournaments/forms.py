from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        if cd["start_time"] < timezone.now():
            raise ValidationError("A Tournament cannot take place in the past!")
        if cd["include_users"].count() < 2:
            raise ValidationError("A Tournament must include at least 2 players!")
        if (
            cd["include_users"].filter(username="Yourself").exists()
            or cd["bye_player"].username == "Yourself"
        ):
            raise ValidationError('The "Yourself" player cannot participate in Tournaments!')
        if cd["include_users"].filter(username=cd["bye_player"].username).exists():
            raise ValidationError("The bye player cannot participate in the Tournament!")

    class Meta:
        model = Tournament
        exclude = ("finished", "terminated", "played")
        labels = {"include_users": "Include Users: ", "bye_player": "Bye Player: "}


class TournamentManagementForm(forms.Form):

    terminate = forms.BooleanField()
    remove_users = forms.ModelMultipleChoiceField(queryset=None, widget=forms.HiddenInput())

    def __init__(self, tournament, *args, **kwargs):
        super(TournamentManagementForm, self).__init__(*args, **kwargs)
        self.status = "future" if tournament in Tournament.objects.future() else "in_progress"

        players = tournament.players.all()
        self.fields["remove_users"].queryset = players

        if self.status == "future":
            self.fields["terminate"].label = "Delete Tournament: "
            self.fields["reschedule"] = forms.DateTimeField(
                label="Reschedule: ",
                input_formats=settings.DATE_INPUT_FORMATS,
                widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
            )

            self.fields["num_rounds"] = forms.IntegerField(
                min_value=15, max_value=settings.MAX_ROUND_NUM
            )
            self.fields["game_time_limit"] = forms.IntegerField(min_value=1, max_value=15)
            self.fields["bye_user"] = forms.ModelChoiceField(queryset=players)
            self.fields["add_users"] = forms.ModelMultipleChoiceField(
                queryset=get_user_model().objects.all()
            )
        else:
            self.fields["terminate"].label = "Terminate Tournament: "

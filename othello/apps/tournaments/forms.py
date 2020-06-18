from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Tournament
from ..games.models import Submission

User = get_user_model()


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
        if Submission.objects.latest(user_id__in=cd["include_users"], is_legacy=True).exists():
            cd["using_legacy"] = True

    class Meta:
        model = Tournament
        exclude = ("finished", "terminated", "played")
        labels = {"include_users": "Include Users: ", "bye_player": "Bye Player: "}


class TournamentManagementForm(forms.Form):
    terminate = forms.BooleanField(required=False)
    remove_users = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, tournament, *args, **kwargs):
        super(TournamentManagementForm, self).__init__(*args, **kwargs)
        self.tournament = tournament
        self.status = "future" if tournament in Tournament.objects.future() else "in_progress"

        players = tournament.include_users.all()
        self.fields["remove_users"].queryset = players

        if self.status == "future":
            self.fields["terminate"].label = "Delete Tournament: "
            self.fields["reschedule"] = forms.DateTimeField(
                label="Reschedule: ",
                input_formats=settings.DATE_INPUT_FORMATS,
                widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
                required=False,
            )

            self.fields["num_rounds"] = forms.IntegerField(
                max_value=settings.MAX_ROUND_NUM, required=False
            )
            self.fields["game_time_limit"] = forms.IntegerField(
                min_value=1, max_value=15, required=False
            )
            self.fields["bye_user"] = forms.ModelChoiceField(
                queryset=User.objects.all(), required=False
            )
            self.fields["add_users"] = forms.ModelMultipleChoiceField(
                queryset=User.objects.all(), required=False
            )
        else:
            self.fields["terminate"].label = "Terminate Tournament: "

    def clean(self):
        cd = self.cleaned_data
        if self.status == "future":
            if cd.get("reschedule", False) and cd["reschedule"] < timezone.now():
                raise ValidationError("A Tournament cannot take place in the past!")

            if cd.get("num_rounds", False) and (cd["num_rounds"] < 15 or cd["num_rounds"] > 60):
                raise ValidationError("Number of rounds must be within 15-60 rounds")

            if cd.get("add_users", False):
                if cd["add_users"].filter(username="Yourself").exists():
                    raise ValidationError(
                        'The "Yourself" player cannot participate in Tournaments!'
                    )

                if cd.get("bye_user", False):
                    if cd["add_users"].filter(id=cd["bye_user"].id).exists():
                        raise ValidationError(
                            "The bye player cannot participate in the Tournament!"
                        )

                if Submission.objects.latest(user_id__in=cd["add_users"], is_legacy=True).exists():
                    cd["using_legacy"] = True

            if cd.get("bye_player", False):
                if self.tournament.include_users.filter(id=cd["bye_user"].id).exists():
                    raise ValidationError(
                        "Cannot set a bye player that is already participating in the Tournament"
                    )
                if cd["bye_user"].username == "Yourself":
                    raise ValidationError(
                        'The "Yourself" player cannot participate in Tournaments!'
                    )
                if Submission.objects.latest(user_id__in=cd["bye_player"], is_legacy=True).exists():
                    cd["using_legacy"] = True

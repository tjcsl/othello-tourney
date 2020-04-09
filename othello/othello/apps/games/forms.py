from tempfile import NamedTemporaryFile

from django import forms
from django.core.exceptions import ValidationError

from .utils import import_strategy
from .models import Game, Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('code', )

    def clean(self):
        cd = self.cleaned_data
        with NamedTemporaryFile('r+') as f:
            for chunk in cd['code'].chunks():
                f.write(chunk.decode())
            f.read()
            try:
                import_strategy(f.name)
            except SyntaxError:
                raise ValidationError("File has invalid syntax")
            except AttributeError:
                raise ValidationError("Cannot find attribute Strategy.best_strategy in file")
            except AssertionError:
                raise ValidationError("Attribute Strategy.best_strategy has an invalid amount of parameters")

        return cd


class GameForm(forms.Form):
    choices = Submission.objects.all_latest_submissions()
    black = forms.ModelChoiceField(label="Black:", queryset=choices, initial="Yourself")
    white = forms.ModelChoiceField(label="White:", queryset=choices, initial="Yourself")
    time_limit = forms.IntegerField(label="Time Limit (secs):", initial=5, min_value=1)


class WatchForm(forms.Form):
    games = forms.ModelChoiceField(label="Running Games:", queryset=Game.objects.get_all_running())

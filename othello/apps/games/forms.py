from tempfile import NamedTemporaryFile

from django import forms
from django.core.exceptions import ValidationError

from .models import Submission
from ...sandboxing import import_strategy_sandboxed


class SubmissionForm(forms.ModelForm):
    name = forms.CharField(required=False)
    code = forms.FileField(required=True)

    class Meta:
        model = Submission
        fields = ('name', 'code',)

    def clean(self):
        cd = self.cleaned_data
        if not cd['name']:
            cd['name'] = cd["code"].name
        with NamedTemporaryFile('wb+') as f:
            for chunk in cd['code'].chunks():
                f.write(chunk)
            f.read()  # for some reason importlib cannot read the file unless we do f.read first
            if (errs := import_strategy_sandboxed(f.name)) != 0:
                raise ValidationError(errs['message'])

        return cd


class ChangeSubmissionForm(forms.Form):
    new_script = forms.ModelChoiceField(
        label="Change current AI:",
        queryset=None,
    )

    def __init__(self, user, *args, **kwargs):
        super(ChangeSubmissionForm, self).__init__(*args, **kwargs)
        choices = Submission.objects.filter(user=user)
        self.fields["new_script"].queryset = choices
        self.fields["new_script"].initial = choices[0] if len(choices) >= 1 else None
        self.fields["new_script"].label_from_instance = lambda obj: f"{obj.get_submission_name()}"


class GameForm(forms.Form):
    choices = Submission.objects.usable()
    black = forms.ModelChoiceField(label="Black:", queryset=choices, initial="Yourself")
    white = forms.ModelChoiceField(label="White:", queryset=choices, initial="Yourself")
    time_limit = forms.IntegerField(label="Time Limit (secs):", initial=5, min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['black'].label_from_instance = lambda obj: obj.get_user_name()
        self.fields['white'].label_from_instance = lambda obj: obj.get_user_name()


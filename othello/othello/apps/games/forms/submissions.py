from tempfile import NamedTemporaryFile

from django import forms
from django.core.exceptions import ValidationError

from ..utils import import_strategy
from ..models import Submission


class SubmissionForm(forms.ModelForm):

    name = forms.CharField(required=False)
    code = forms.FileField(required=True)

    class Meta:
        model = Submission
        fields = ('name', 'code', )

    def clean(self):
        cd = self.cleaned_data
        if not cd['name']:
            cd['name'] = cd["code"].name
        with NamedTemporaryFile('wb+') as f:
            for chunk in cd['code'].chunks():
                f.write(chunk)
            f.read()  # for some reason importlib cannot read the file unless we do f.read first
            try:
                import_strategy(f.name)
            except SyntaxError:
                raise ValidationError("File has invalid syntax")
            except AttributeError:
                raise ValidationError("Cannot find attribute Strategy.best_strategy in file")
            except AssertionError:
                raise ValidationError("Attribute Strategy.best_strategy has an invalid amount of parameters")

        return cd


class ChangeSubmissionForm(forms.Form):
    new_script = forms.ModelChoiceField(
        label="Change current AI:",
        queryset=None,
    )

    def __init__(self, user, *args, **kwargs):
        super(ChangeSubmissionForm, self).__init__(*args, **kwargs)
        choices = Submission.objects.get_all_submissions_for_user(user=user)
        self.fields["new_script"].queryset = choices
        self.fields["new_script"].initial = choices[0]
        self.fields["new_script"].label_from_instance = lambda obj: f"{obj.get_submission_name()}"

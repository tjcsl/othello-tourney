from tempfile import NamedTemporaryFile

from django import forms
from django.core.exceptions import ValidationError

from ..utils import import_strategy
from ..models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('code', )

    def clean(self):
        cd = self.cleaned_data
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


from django import forms


class MultipleChoiceForm(forms.Form):
    CHOICES = [
        ("deletegames", "Delete all ranked games models"),
        ("deletegauntlets", "Delete all gauntlet models"),
        ("disableauto", "Disable auto ranked games (also terminates if current)"),
        ("enableauto", "Enable auto ranked games"),
        ("initranked", "Initialize ranked (when the server starts for the first time)"),
    ]

    choices = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)

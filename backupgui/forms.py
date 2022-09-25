from django import forms
from .models import BackupSets, LogLevel


# create a ModelForm
class BackupSetsForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = BackupSets
        fields = "__all__"


class LogLevelForm(forms.Form):
    ll_choices = LogLevel.llChoices()
    LOGLEVEL_CHOICES = forms.ChoiceField(
        choices=ll_choices
    )


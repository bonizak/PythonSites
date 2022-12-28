from django import forms

from .models import BackupSets, RootPaths, LoggingLevels


# create a ModelForm
class BackupSetsForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = BackupSets
        fields = "__all__"


class LogLevelForm(forms.Form):
    ll_choices = LoggingLevels.llChoices()
    LOGLEVEL_CHOICES = forms.ChoiceField(
        choices=ll_choices
    )


class RootPathsForm(forms.Form):
    rp_choices = RootPaths.rpChoices()
    ROOTPATH_CHOICES = forms.ChoiceField(
        choices=rp_choices
    )

from django import forms
from django.utils.translation import gettext_lazy as _

from flase_app.models import Owner


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ["name"]

        labels = {
            "name": _("Name"),
        }

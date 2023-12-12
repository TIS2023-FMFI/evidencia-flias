from django import forms
from django.utils.translation import gettext_lazy as _

from flase_app.models import Owner
from flase_app.models import User

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ["name"]

        labels = {
            "name": _("Name"),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username","role"]
        widgets = {
            'password': forms.PasswordInput(),
            'email': forms.EmailInput(),
            }
        labels = {
            "role": _("Role"),
            "username": _("Username"),
            "password": _("Password"),
            "email": _("Email"),
        }

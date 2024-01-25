from django import forms
from django.utils.translation import gettext_lazy as _

from flase_app.models import Owner, Supplier
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
        fields = ["username","password", "email", "role", "is_active"]
        widgets = {
            'password': forms.PasswordInput(),
            'email': forms.EmailInput(),
            }
        labels = {
            "role": _("Role"),
            "username": _("Username"),
            "password": _("Password"),
            "email": _("Email"),
            "is_active": _("Is Active"),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name"]
        labels = {
            "name": _("Name"),
        }




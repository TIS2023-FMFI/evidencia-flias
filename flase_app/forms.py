from django import forms
from django.utils.translation import gettext_lazy as _

from flase_app.models import Owner, User, CylinderLife, Cylinder, Supplier, \
    CylinderChange, Location, Gas

from flase_app.models import Owner, Supplier, CylinderLife
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


class CylinderLifeForm(forms.ModelForm):
    barcode = forms.CharField(max_length=64)
    owner = forms.ModelChoiceField(queryset=Owner.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance:
            self.fields['barcode'].initial = instance.cylinder.barcode
            self.fields['owner'].initial = instance.cylinder.owner

        self.fields['owner'].required = False

    def save(self, commit = True):
        cylinder, created = Cylinder.objects.get_or_create(barcode=self.cleaned_data["barcode"], defaults={"owner": self.cleaned_data["owner"]})
        life = super().save(commit=False)
        if (not created):
            cylinder.owner = self.cleaned_data["owner"]
            cylinder.save()
        life.cylinder = cylinder
        life.save()

        return life

    class Meta:
        model = CylinderLife
        fields = ["barcode", "owner", "volume", "supplier", "pressure", "location", "is_connected", "gas", "note", "is_current"]
        widgets = {
            'note': forms.Textarea(attrs={'cols': 40, 'rows': 5}),
        }
        labels = {
            "barcode": _("Barcode"),
            "owner": _("Owner"),
            "volume": _("Volume"),
            "supplier": _("Supplier"),
            "pressure": _("Pressure"),
            "location": _("Location"),
            "is_connected": _("Is_connected"),
            "gas": _("Gas"),
            "note": _("Note"),
            "is_current": _("Is_current"),
        }


class PressureLogForm(forms.ModelForm):
    class Meta:
        model = CylinderChange
        fields = ["pressure"]
        labels = {
            "pressure": _("Current pressure"),
        }


class CylinderFilterForm(forms.Form):
    gas = forms.ModelChoiceField(queryset=Gas.objects.all(), required=False)
    owner = forms.ModelChoiceField(queryset=Owner.objects.all(), required=False)
    volume = forms.DecimalField(required=False)
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), required=False)
    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False)
    status = forms.ChoiceField(choices=[(True, 'Connected'), (False, 'Not Connected')], required=False, widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super(CylinderFilterForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = [('', 'Any'),] + list(self.fields['status'].choices)[1:]


class CylinderLifeForm2(forms.ModelForm):
    owner = forms.ModelChoiceField(Owner.objects, label=_("Owner"))

    field_order = ["gas", "volume", "owner", "supplier", "note"]

    class Meta:
        model = CylinderLife
        fields = ["gas", "volume", "supplier", "note"]
        labels = {
            "gas": _("Gas"),
            "volume": _("Volume"),
            "supplier": _("Supplier"),
            "note": _("Note"),
        }

        widgets = {
            "note": forms.Textarea()
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["owner"].initial = self.instance.cylinder.owner

    def save(self, commit=True):
        life = super().save(commit=commit)
        cylinder = life.cylinder
        cylinder.owner = self.cleaned_data["owner"]
        cylinder.save()
        # we should not save if commit=False, but there is no good way to indicate
        # that there are multiple models changed to the caller, so we save it anyway
        return life

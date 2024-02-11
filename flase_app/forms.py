from django import forms
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from flase_app.models import (
    Owner,
    User,
    CylinderLife,
    Cylinder,
    Supplier,
    CylinderChange,
    Location,
    Gas,
    Workplace,
    Building,
)


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "workplace", "person_responsible"]
        labels = {
            "name": _("Name"),
            "workplace": _("Workplace"),
            "person_responsible": _("Person responsible"),
        }

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ["name"]
        labels = {
            "name": _("Name"),
        }

class WorkplaceForm(forms.ModelForm):
    class Meta:
        model = Workplace
        fields = ["name", "building"]
        labels = {
            "name": _("Name"),
            "building": _("Building"),
        }

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ["name"]

        labels = {
            "name": _("Name"),
        }


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text=_("Leave empty if you want to keep the current password."),
        label=_("Password"),
    )

    field_order = ["first_name", "last_name", "email", "password", "role", "is_active"]

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "role", "is_active"]
        labels = {
            "first_name": _("First name"),
            "last_name": _("Last name"),
            "email": _("Email address"),
            "role": _("Role"),
            "is_active": _("Active"),
        }

        help_texts = {
            "is_active": _(
                "Use this to disable users. An inactive user cannot log in."
            ),
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not kwargs.get("instance"):
            self.fields["password"].required = True
            self.fields["password"].help_text = ""

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if password:
            validate_password(password)

        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name"]
        labels = {
            "name": _("Name"),
        }


class CylinderLifeCreateForm(forms.ModelForm):
    barcode = forms.CharField(max_length=64, label=_("Barcode"))
    owner = forms.ModelChoiceField(queryset=Owner.objects.get_queryset(), required=False, label=_("Owner"))

    field_order = ["barcode", "gas", "volume", "owner", "supplier", "pressure", "location", "is_connected", "note"]

    class Meta:
        model = CylinderLife
        fields = [
            "gas",
            "volume",
            "supplier",
            "note",
            "location",
            "is_connected",
            "pressure",
        ]
        widgets = {
            "note": forms.Textarea(),
        }
        labels = {
            "volume": _("Volume"),
            "supplier": _("Supplier"),
            "pressure": _("Pressure"),
            "location": _("Location"),
            "is_connected": _("Connected"),
            "gas": _("Gas"),
            "note": _("Note"),
        }

    def __init__(self, **kwargs):
        self.user = kwargs.pop("user")
        cylinder = kwargs.pop("cylinder")
        super().__init__(**kwargs)

        if cylinder:
            self.fields["barcode"].initial = cylinder.barcode
            self.fields["owner"].initial = cylinder.owner

            latest_life = cylinder.cylinderlife_set.filter(is_current=True).first()
            if latest_life:
                self.fields["gas"].initial = latest_life.gas
                self.fields["volume"].initial = latest_life.volume
                self.fields["supplier"].initial = latest_life.supplier

    @transaction.atomic
    def save(self, commit=True):
        cylinder, created = Cylinder.objects.get_or_create(
            barcode=self.cleaned_data["barcode"],
            defaults={"owner": self.cleaned_data["owner"]},
        )
        life = super().save(commit=False)
        if not created:
            cylinder.owner = self.cleaned_data["owner"]
            cylinder.save()

        cylinder.cylinderlife_set.filter(is_current=True).update(is_current=False, end_date=timezone.now())

        life.cylinder = cylinder
        life.is_current = True
        life.start_date = timezone.now()
        life.save()

        location = self.cleaned_data.get("location")
        is_connected = self.cleaned_data.get("is_connected")
        pressure = self.cleaned_data.get("pressure")

        if location or pressure or is_connected is not None:
            change = CylinderChange(life=life, user=self.user)
            change.pressure = pressure
            change.location = location
            change.is_connected = is_connected
            change.save()

        return life



class PressureLogForm(forms.ModelForm):
    class Meta:
        model = CylinderChange
        fields = ["pressure"]
        labels = {
            "pressure": _("Current pressure"),
        }


class RelocateForm(forms.ModelForm):
    class Meta:
        model = CylinderChange
        fields = ["location", "is_connected"]
        labels = {
            "location": _("Location"),
            "is_connected": _("Connected"),
        }

        widgets = {
            "is_connected": forms.CheckboxInput(),
        }

    def __init__(self, **kwargs):
        self.life = kwargs.pop("life")
        self.user = kwargs.pop("user")
        super().__init__(**kwargs)

        self.fields["location"].required = True
        self.fields["location"].initial = self.life.location
        self.fields["is_connected"].initial = self.life.is_connected

    def save(self, commit=True):
        change = super().save(commit=False)
        change.user = self.user
        change.life = self.life
        change.save()

        self.life.location = self.cleaned_data["location"]
        self.life.is_connected = self.cleaned_data["is_connected"]
        self.life.save()

        return change


class CylinderFilterForm(forms.Form):
    query = forms.CharField(label=_("Search query"), required=False)
    gas = forms.ModelChoiceField(queryset=Gas.objects.get_queryset(), required=False, label=_("Gas"))
    owner = forms.ModelChoiceField(queryset=Owner.objects.get_queryset(), required=False, label=_("Owner"))
    volume = forms.DecimalField(required=False, label=_("Volume"))
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.get_queryset(), required=False, label=_("Supplier"))
    location = forms.ModelChoiceField(queryset=Location.objects.get_queryset(), required=False, label=_("Location"))
    status = forms.ChoiceField(
        choices=[("", "---------"), ("c", _("Connected")), ("d", _("Disconnected"))],
        required=False,
        widget=forms.Select(),
        label=_("Status"),
    )
    building = forms.ModelChoiceField(queryset=Building.objects.get_queryset(), required=False, label=_("Building"))
    workplace = forms.ModelChoiceField(queryset=Workplace.objects.get_queryset(), required=False, label=_("Workplace"))


class CylinderLifeUpdateForm(forms.ModelForm):
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

        widgets = {"note": forms.Textarea()}

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


class GasForm(forms.ModelForm):
    class Meta:
        model = Gas
        fields = ["name", "note"]


class BarcodeForm(forms.Form):
    barcode = forms.CharField(max_length=64)

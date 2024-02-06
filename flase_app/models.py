from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.IntegerChoices):
        ADMIN = 0, _("Admin")
        EDITOR = 1, _("Editor")
        READER = 2, _("Reader")

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.IntegerField(choices=Role.choices, default=Role.READER)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name


class Owner(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Workplace(models.Model):
    name = models.CharField(max_length=128)
    building = models.ForeignKey(Building, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.name}, {self.building.name}"


class Location(models.Model):
    name = models.CharField(max_length=128)
    workplace = models.ForeignKey(Workplace, on_delete=models.RESTRICT)
    person_responsible = models.CharField(max_length=128)
    # TODO: manometer?

    def __str__(self):
        return f"{self.name}, {self.workplace.name}, {self.workplace.building.name}"


class Cylinder(models.Model):
    barcode = models.CharField(max_length=64, unique=True)
    owner = models.ForeignKey(Owner, on_delete=models.RESTRICT, blank=True, null=True)


class Gas(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class CylinderLife(models.Model):
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.RESTRICT, blank=True, null=True
    )

    pressure = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.RESTRICT)
    is_connected = models.BooleanField()
    gas = models.ForeignKey(Gas, on_delete=models.RESTRICT, blank=True, null=True)
    note = models.CharField(max_length=256, blank=True)

    is_current = models.BooleanField()
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    # stav?
    # dat. prevzatie
    # dat. zapojenie
    # dat. odovzdanie?


class CylinderChange(models.Model):
    life = models.ForeignKey(CylinderLife, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)

    pressure = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(
        Location, on_delete=models.RESTRICT, blank=True, null=True
    )
    is_connected = models.BooleanField(blank=True, null=True)
    note = models.CharField(max_length=256, blank=True, null=True)

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Owner(models.Model):
    name = models.CharField(max_length=128)


class Supplier(models.Model):
    name = models.CharField(max_length=128)


class Building(models.Model):
    name = models.CharField(max_length=128)


class Workplace(models.Model):
    name = models.CharField(max_length=128)
    building = models.ForeignKey(Building, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.building.name} / {self.name}"


class Location(models.Model):
    name = models.CharField(max_length=128)
    workplace = models.ForeignKey(Workplace, on_delete=models.RESTRICT)
    person_responsible = models.CharField(max_length=128)
    # TODO: manometer?


class Cylinder(models.Model):
    barcode = models.CharField(max_length=64, unique=True)
    owner = models.ForeignKey(Owner, on_delete=models.RESTRICT)


class Gas(models.Model):
    name = models.CharField(max_length=128)


class CylinderLife(models.Model):
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=6, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.RESTRICT, blank=True, null=True)

    pressure = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.RESTRICT)
    is_connected = models.BooleanField()
    gas = models.ForeignKey(Gas, on_delete=models.RESTRICT)
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
    location = models.ForeignKey(Location, on_delete=models.RESTRICT, blank=True, null=True)
    is_connected = models.BooleanField(blank=True, null=True)
    note = models.CharField(max_length=256, blank=True, null=True)


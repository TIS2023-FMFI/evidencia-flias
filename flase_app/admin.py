from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Owner, Supplier, Building, Workplace, Location, Cylinder, Gas, CylinderLife, CylinderChange

admin.site.register(User, UserAdmin)


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    pass


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "workplace"]
	
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ["name"]

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name"]

# @admin.register(Building)
# class BuildingAdmin(admin.ModelAdmin):
#     list_display = ["name"]
#
# @admin.register(Workplace)
# class WorkplaceAdmin(admin.ModelAdmin):
#     list_display = ["name", "building"]
#
# @admin.register(Location)
# class LocationAdmin(admin.ModelAdmin):
#     list_display = ["name", "workplace", "person_responsible"]

@admin.register(Cylinder)
class CylinderAdmin(admin.ModelAdmin):
    list_display = ["barcode", "owner"]

@admin.register(Gas)
class GasAdmin(admin.ModelAdmin):
    list_display = ["name"]

@admin.register(CylinderLife)
class CylinderLifeAdmin(admin.ModelAdmin):
    list_display = ["cylinder", "volume", "supplier", "pressure", "location", "is_connected", "gas", "is_current", "start_date", "end_date"]

@admin.register(CylinderChange)
class CylinderChangeAdmin(admin.ModelAdmin):
    list_display = ["life", "timestamp", "user", "pressure", "location", "is_connected"]

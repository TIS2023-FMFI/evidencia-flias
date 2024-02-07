from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import (
    User,
    Owner,
    Supplier,
    Building,
    Workplace,
    Location,
    Cylinder,
    Gas,
    CylinderLife,
    CylinderChange,
)


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "role",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ["name", "building"]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "workplace", "person_responsible"]


@admin.register(Cylinder)
class CylinderAdmin(admin.ModelAdmin):
    list_display = ["barcode", "owner"]


@admin.register(Gas)
class GasAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(CylinderLife)
class CylinderLifeAdmin(admin.ModelAdmin):
    list_display = [
        "cylinder",
        "volume",
        "supplier",
        "pressure",
        "location",
        "is_connected",
        "gas",
        "is_current",
        "start_date",
        "end_date",
    ]


@admin.register(CylinderChange)
class CylinderChangeAdmin(admin.ModelAdmin):
    list_display = ["life", "timestamp", "user", "pressure", "location", "is_connected"]

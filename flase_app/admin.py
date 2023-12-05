from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Location, Building, Workplace

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

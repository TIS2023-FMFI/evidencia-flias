from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView

from flase_app.forms import WorkplaceForm, BuildingForm, LocationForm
from flase_app.mixins import RestrictedDeleteView, AdminRequiredMixin
from flase_app.models import Workplace, Building, Location


class WorkplaceListView(AdminRequiredMixin, ListView):
    model = Workplace
    template_name = "places/workplaces.html"


class WorkplaceUpdateView(AdminRequiredMixin, UpdateView):
    model = Workplace
    template_name = "places/workplaces_form.html"
    form_class = WorkplaceForm

    def get_success_url(self):
        return reverse("workplace_list")


class WorkplaceCreateView(AdminRequiredMixin, CreateView):
    model = Workplace
    template_name = "places/workplaces_form.html"
    form_class = WorkplaceForm

    def get_success_url(self):
        return reverse("workplace_list")


class WorkplaceDeleteView(AdminRequiredMixin, RestrictedDeleteView):
    model = Workplace
    template_name = "places/workplaces_delete.html"

    def get_success_url(self):
        return reverse("workplace_list")


class BuildingListView(AdminRequiredMixin, ListView):
    model = Building
    template_name = "places/buildings.html"


class BuildingUpdateView(AdminRequiredMixin, UpdateView):
    model = Building
    template_name = "places/buildings_form.html"
    form_class = BuildingForm

    def get_success_url(self):
        return reverse("building_list")


class BuildingCreateView(AdminRequiredMixin, CreateView):
    model = Building
    template_name = "places/buildings_form.html"
    form_class = BuildingForm

    def get_success_url(self):
        return reverse("building_list")

class BuildingDeleteView(AdminRequiredMixin, RestrictedDeleteView):
    model = Building
    template_name = "places/buildings_delete.html"

    def get_success_url(self):
        return reverse("building_list")


class LocationListView(AdminRequiredMixin, ListView):
    model = Location
    template_name = "places/locations.html"


class LocationUpdateView(AdminRequiredMixin, UpdateView):
    model = Location
    template_name = "places/locations_form.html"
    form_class = LocationForm

    def get_success_url(self):
        return reverse("location_list")


class LocationCreateView(AdminRequiredMixin, CreateView):
    model = Location
    template_name = "places/locations_form.html"
    form_class = LocationForm

    def get_success_url(self):
        return reverse("location_list")


class LocationDeleteView(AdminRequiredMixin, RestrictedDeleteView):
    model = Location
    template_name = "places/locations_delete.html"

    def get_success_url(self):
        return reverse("location_list")

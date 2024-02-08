from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from flase_app.forms import WorkplaceForm, BuildingForm, LocationForm
from flase_app.mixins import RestrictedDeleteView
from flase_app.models import Workplace, Building, Location


class WorkplaceListView(LoginRequiredMixin, ListView):
    model = Workplace
    template_name = "places/workplaces.html"


class WorkplaceUpdateView(LoginRequiredMixin, UpdateView):
    model = Workplace
    template_name = "places/workplaces_form.html"
    form_class = WorkplaceForm

    def get_success_url(self):
        return reverse("workplace_list")


class WorkplaceCreateView(LoginRequiredMixin, CreateView):
    model = Workplace
    template_name = "places/workplaces_form.html"
    form_class = WorkplaceForm

    def get_success_url(self):
        return reverse("workplace_list")


class WorkplaceDeleteView(LoginRequiredMixin, RestrictedDeleteView):
    model = Workplace
    template_name = "places/workplaces_delete.html"

    def get_success_url(self):
        return reverse("workplace_list")


class BuildingListView(LoginRequiredMixin, ListView):
    model = Building
    template_name = "places/buildings.html"


class BuildingUpdateView(LoginRequiredMixin, UpdateView):
    model = Building
    template_name = "places/buildings_form.html"
    form_class = BuildingForm

    def get_success_url(self):
        return reverse("building_list")


class BuildingCreateView(LoginRequiredMixin, CreateView):
    model = Building
    template_name = "places/buildings_form.html"
    form_class = BuildingForm

    def get_success_url(self):
        return reverse("building_list")

class BuildingDeleteView(LoginRequiredMixin, RestrictedDeleteView):
    model = Building
    template_name = "places/buildings_delete.html"

    def get_success_url(self):
        return reverse("building_list")


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "places/locations.html"


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    template_name = "places/locations_form.html"
    form_class = LocationForm

    def get_success_url(self):
        return reverse("location_list")


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    template_name = "places/locations_form.html"
    form_class = LocationForm

    def get_success_url(self):
        return reverse("location_list")


class LocationDeleteView(LoginRequiredMixin, RestrictedDeleteView):
    model = Location
    template_name = "places/locations_delete.html"

    def get_success_url(self):
        return reverse("location_list")

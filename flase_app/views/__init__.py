from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import UpdateView, CreateView

from flase_app.forms import (
    CylinderLifeForm,
    PressureLogForm,
    CylinderLifeForm2,
)
from flase_app.models import CylinderLife


class CylinderCreateView(LoginRequiredMixin, CreateView):
    template_name = "cylinders/create.html"
    form_class = CylinderLifeForm

    def get_success_url(self):
        return reverse("cylinder_list")


class CylinderUpdateView(LoginRequiredMixin, UpdateView):
    model = CylinderLife
    template_name = "cylinders/create.html"
    form_class = CylinderLifeForm

    def get_success_url(self):
        return reverse("cylinder_list")


class PressureLogView(LoginRequiredMixin, CreateView):
    form_class = PressureLogForm
    template_name = "cylinders/log_pressure.html"

    @cached_property
    def cylinder_life(self):
        return get_object_or_404(CylinderLife, id=self.kwargs["pk"])

    def get_initial(self):
        initial = super().get_initial()
        initial["pressure"] = self.cylinder_life.pressure
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["life"] = self.cylinder_life
        return ctx

    def form_valid(self, form):
        change = form.save(commit=False)
        change.user = self.request.user
        change.life = self.cylinder_life
        change.save()

        life = self.cylinder_life
        life.pressure = change.pressure
        life.save()

        return HttpResponseRedirect("/")  # TODO: redirect to cylinder life detail


class CylinderLifeUpdateView(LoginRequiredMixin, UpdateView):
    model = CylinderLife
    form_class = CylinderLifeForm2
    template_name = "cylinder_life/form.html"

    def get_success_url(self):
        return "/"  # TODO: redirect to cylinder detail page

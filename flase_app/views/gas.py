# flase_app/views/gas.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView

from flase_app.forms import GasForm
from flase_app.mixins import RestrictedDeleteView
from flase_app.models import Gas


class GasListView(LoginRequiredMixin, ListView):
    model = Gas
    template_name = "gasses/list.html"


class GasUpdateView(LoginRequiredMixin, UpdateView):
    model = Gas
    template_name = "gasses/form.html"
    form_class = GasForm

    def get_success_url(self):
        return reverse("gas_list")


class GasCreateView(LoginRequiredMixin, CreateView):
    model = Gas
    template_name = "gasses/form.html"
    form_class = GasForm

    def get_success_url(self):
        return reverse("gas_list")


class GasDeleteView(LoginRequiredMixin, RestrictedDeleteView):
    model = Gas
    template_name = "gasses/delete.html"

    def get_success_url(self):
        return reverse("gas_list")

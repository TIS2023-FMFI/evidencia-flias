from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from flase_app.forms import SupplierForm
from flase_app.models import Supplier


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = "suppliers/list.html"


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/form.html"

    def get_success_url(self):
        return reverse("supplier_list")


class SupplierCreateView(LoginRequiredMixin, CreateView):
    form_class = SupplierForm
    template_name = "suppliers/form.html"

    def get_success_url(self):
        return reverse("supplier_list")


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = "suppliers/delete.html"

    def get_success_url(self):
        return reverse("supplier_list")

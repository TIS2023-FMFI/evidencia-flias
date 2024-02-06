from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from flase_app.forms import OwnerForm
from flase_app.mixins import AdminRequiredMixin
from flase_app.models import Owner


class OwnerListView(AdminRequiredMixin, ListView):
    model = Owner
    template_name = "owners/list.html"


class OwnerUpdateView(AdminRequiredMixin, UpdateView):
    model = Owner
    template_name = "owners/form.html"
    form_class = OwnerForm

    def get_success_url(self):
        return reverse("owner_list")


class OwnerCreateView(AdminRequiredMixin, CreateView):
    template_name = "owners/form.html"
    form_class = OwnerForm

    def get_success_url(self):
        return reverse("owner_list")


class OwnerDeleteView(AdminRequiredMixin, DeleteView):
    model = Owner
    template_name = "owners/delete.html"

    def get_success_url(self):
        return reverse("owner_list")

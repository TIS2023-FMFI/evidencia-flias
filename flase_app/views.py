from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from flase_app.forms import OwnerForm, SupplierForm
from flase_app.models import Owner, Supplier

from flase_app.forms import UserForm
from flase_app.models import User

class OwnerListView(LoginRequiredMixin, ListView):
    model = Owner
    template_name = "owners/list.html"


class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Owner
    template_name = "owners/update.html"
    form_class = OwnerForm

    def get_success_url(self):
        return reverse("owner_list")


class OwnerCreateView(LoginRequiredMixin, CreateView):
    template_name = "owners/update.html"
    form_class = OwnerForm

    def get_success_url(self):
        return reverse("owner_list")


class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    model = Owner
    template_name = "owners/delete.html"

    def get_success_url(self):
        return reverse("owner_list")


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/list.html"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "users/update.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse("user_list")


class UserCreateView(LoginRequiredMixin, CreateView):
    template_name = "users/update.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse("user_list")


class UserDisableView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "users/disable.html"

    def get_success_url(self):
        return reverse("user_list")


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

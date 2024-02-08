from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from flase_app.forms import UserForm
from flase_app.mixins import AdminRequiredMixin
from flase_app.models import User


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "users/list.html"


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    template_name = "users/form.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse("user_list")


class UserCreateView(AdminRequiredMixin, CreateView):
    template_name = "users/form.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse("user_list")

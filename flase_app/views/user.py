from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from flase_app.forms import UserForm
from flase_app.models import User


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/list.html"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "users/form.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse("user_list")


class UserCreateView(LoginRequiredMixin, CreateView):
    template_name = "users/form.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse("user_list")


class UserDisableView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "users/disable.html"

    def get_success_url(self):
        return reverse("user_list")

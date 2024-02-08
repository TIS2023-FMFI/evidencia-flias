from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import RestrictedError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DeleteView

from flase_app.models import User


class RoleRequiredMixin(UserPassesTestMixin):
    """
    Denies request if user does not have the required role.
    """
    role = User.Role.READER

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role >= self.role


class AdminRequiredMixin(RoleRequiredMixin):
    role = User.Role.ADMIN


class OperatorRequiredMixin(RoleRequiredMixin):
    role = User.Role.OPERATOR


class EditorRequiredMixin(RoleRequiredMixin):
    role = User.Role.EDITOR


class RestrictedDeleteView(DeleteView):
    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except RestrictedError:
            return render(self.request, "delete_restricted.html", {"success_url": self.get_success_url()})

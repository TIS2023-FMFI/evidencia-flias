from django.contrib.auth.mixins import UserPassesTestMixin

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

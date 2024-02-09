from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth import logout
from django.shortcuts import redirect


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'registration/password_change.html'
    
    def get_success_url(self):
        return reverse("password_change_done")


def CustomLogoutView(request):
    logout(request)
    return redirect('login')

from django.urls import reverse
from django.views.generic import ListView, UpdateView

from flase_app.forms import AlertForm
from flase_app.mixins import AdminRequiredMixin
from flase_app.models import Alert


class AlertListView(AdminRequiredMixin, ListView):
    model = Alert
    template_name = "alerts/list.html"


class AlertUpdateView(AdminRequiredMixin, UpdateView):
    model = Alert
    template_name = "alerts/form.html"
    form_class = AlertForm

    def get_success_url(self):
        return reverse("alert_list")

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import SpravaPlynov
from .forms import SpravaPlynovForm

class ZoznamPlynovView(ListView):
    model = SpravaPlynov
    template_name = 'flase_app/zoznam_plynov.html'
    context_object_name = 'plynov'

class PridatPlynView(CreateView):
    model = SpravaPlynov
    form_class = SpravaPlynovForm
    template_name = 'flase_app/form_plynov.html'
    success_url = reverse_lazy('zoznam_plynov')

class UpravitPlynView(UpdateView):
    model = SpravaPlynov
    form_class = SpravaPlynovForm
    template_name = 'flase_app/form_plynov.html'
    success_url = reverse_lazy('zoznam_plynov')

class VymazatPlynView(DeleteView):
    model = SpravaPlynov
    template_name = 'flase_app/confirm_delete_pre_plyny.html'
    success_url = reverse_lazy('zoznam_plynov')

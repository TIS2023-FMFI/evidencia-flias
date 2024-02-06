from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import ListView, UpdateView, CreateView

from flase_app.forms import CylinderLifeForm, \
    PressureLogForm, CylinderFilterForm, CylinderLifeForm2
from flase_app.models import CylinderLife, Cylinder


class CylinderLifeListView(ListView):
    model = CylinderLife
    template_name = "cylinders/index.html"

    def post(self, request, *args, **kwargs):
        barcode = request.POST.get('barcode')
        note = request.POST.get('note')
        # Filter your queryset based on the submitted barcode and note
        self.object_list = CylinderLife.objects.filter(cylinder__barcode__icontains=barcode, note__icontains=note)
        # Return a HttpResponseRedirect or render the template with the filtered queryset
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context


class CylinderListView(LoginRequiredMixin, ListView):
    model = Cylinder
    template_name = 'cylinders/list.html'
    context_object_name = 'cylinders'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = CylinderFilterForm(self.request.GET)
        if form.is_valid():
            gas = form.cleaned_data.get('gas')
            owner = form.cleaned_data.get('owner')
            volume = form.cleaned_data.get('volume')
            supplier = form.cleaned_data.get('supplier')
            location = form.cleaned_data.get('location')
            status = form.cleaned_data.get('status')

            if gas:
                queryset = queryset.filter(cylinderlife__gas=gas, cylinderlife__is_current=True)
            if owner:
                queryset = queryset.filter(owner=owner)
            if volume is not None:
                queryset = queryset.filter(cylinderlife__volume=volume, cylinderlife__is_current=True)
            if supplier:
                queryset = queryset.filter(cylinderlife__supplier=supplier, cylinderlife__is_current=True)
            if location:
                queryset = queryset.filter(cylinderlife__location=location, cylinderlife__is_current=True)
            if status:
                is_connected = status == 'True'
                queryset = queryset.filter(cylinderlife__is_connected=is_connected, cylinderlife__is_current=True)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = CylinderFilterForm(self.request.GET or None)
        return context


class CylinderCreateView(LoginRequiredMixin, CreateView):
    template_name = "cylinders/create.html"
    form_class = CylinderLifeForm

    def get_success_url(self):
        return reverse("cylinder_list")


class CylinderUpdateView(LoginRequiredMixin, UpdateView):
    model = CylinderLife
    template_name = "cylinders/create.html"
    form_class = CylinderLifeForm

    def get_success_url(self):
        return reverse("cylinder_list")


class PressureLogView(LoginRequiredMixin, CreateView):
    form_class = PressureLogForm
    template_name = "cylinders/log_pressure.html"

    @cached_property
    def cylinder_life(self):
        return get_object_or_404(CylinderLife, id=self.kwargs["pk"])

    def get_initial(self):
        initial = super().get_initial()
        initial["pressure"] = self.cylinder_life.pressure
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["life"] = self.cylinder_life
        return ctx

    def form_valid(self, form):
        change = form.save(commit=False)
        change.user = self.request.user
        change.life = self.cylinder_life
        change.save()

        life = self.cylinder_life
        life.pressure = change.pressure
        life.save()

        return HttpResponseRedirect("/") # TODO: redirect to cylinder life detail


class CylinderLifeUpdateView(LoginRequiredMixin, UpdateView):
    model = CylinderLife
    form_class = CylinderLifeForm2
    template_name = "cylinder_life/form.html"

    def get_success_url(self):
        return "/"  # TODO: redirect to cylinder detail page

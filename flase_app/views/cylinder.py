from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView
from django.utils.functional import cached_property

from flase_app.forms import CylinderFilterForm, CylinderLifeUpdateForm, RelocateForm
from flase_app.mixins import OperatorRequiredMixin
from flase_app.models import CylinderLife, CylinderChange
from django.views.generic.detail import DetailView
import csv
from django.http import HttpResponse
from datetime import datetime


class CylinderQuerySetMixin:
    def query_filter(self, qs, query):
        search_object = Q(note__icontains=query)
        search_object |= Q(cylinder__barcode__icontains=query)
        search_object |= Q(cylinder__owner__name__contains=query)
        search_object |= Q(supplier__name__contains=query)
        search_object |= Q(gas__name__contains=query)
        search_object |= Q(location__name__contains=query)
        return qs.filter(search_object)

    def filter_objects(self, qs, form):
        query = form.cleaned_data.get("query")
        if query:
            qs = self.query_filter(qs, query)

        gas = form.cleaned_data.get("gas")
        if gas:
            qs = qs.filter(gas=gas)

        owner = form.cleaned_data.get("owner")
        if owner:
            qs = qs.filter(cylinder__owner=owner)

        volume = form.cleaned_data.get("volume")
        if volume is not None:
            qs = qs.filter(volume=volume)

        supplier = form.cleaned_data.get("supplier")
        if supplier:
            qs = qs.filter(supplier=supplier)

        location = form.cleaned_data.get("location")
        if location:
            qs = qs.filter(location=location)

        status = form.cleaned_data.get("status")
        if status:
            qs = qs.filter(is_connected=(status == "c"))

        return qs

    def get_queryset(self):
        qs = CylinderLife.objects.filter(is_current=True).select_related("cylinder", "gas", "supplier", "location",
                                                                         "location__workplace",
                                                                         "location__workplace__building",
                                                                         "cylinder__owner")

        form = CylinderFilterForm(self.request.GET)
        if form.is_valid():
            qs = self.filter_objects(qs, form)
        return qs


class CylinderListView(LoginRequiredMixin, CylinderQuerySetMixin, ListView):
    model = CylinderLife
    template_name = "cylinders/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = CylinderFilterForm(self.request.GET or None)
        return context


class CylinderExportView(LoginRequiredMixin, CylinderQuerySetMixin, View):
    def get(self, request, *args, **kwargs):
        date = datetime.now().date()
        filename = f"export-cylinders-{date}.csv"
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename=' + filename},
        )

        writer = csv.writer(response)
        writer.writerow(
            ["Gas", "Barcode", "Owner", "Current Location", "Volume", "Supplier", "Notes"])

        # TODO: add remaining data
        for obj in self.get_queryset():
            writer.writerow([
                obj.gas.name,
                obj.cylinder.barcode,
                obj.cylinder.owner.name,
                obj.location.name,
                obj.volume,
                obj.supplier.name,
                obj.note,
            ])

        return response


class CylinderLifeDetailView(DetailView):
    model = CylinderLife
    template_name = 'cylinders/detail.html'
    context_object_name = 'cylinder_life'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cylinder_life_id = self.kwargs.get('pk')
        context['history'] = CylinderChange.objects.filter(life_id=cylinder_life_id).order_by('-timestamp')
        context['deliveries'] = CylinderLife.objects.filter(id=cylinder_life_id).order_by('-start_date')
        return context


class CylinderLifeUpdateView(OperatorRequiredMixin, UpdateView):
    model = CylinderLife
    form_class = CylinderLifeUpdateForm
    template_name = "cylinder_life/form.html"

    def get_success_url(self):
        return reverse('cylinder_life_detail', kwargs={'pk': self.object.id})


class CylinderLifeRelocateView(OperatorRequiredMixin, CreateView):
    form_class = RelocateForm
    template_name = "cylinder_life/relocate.html"

    @cached_property
    def cylinder_life(self):
        return get_object_or_404(CylinderLife, id=self.kwargs["pk"])

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["life"] = self.cylinder_life
        kw["user"] = self.request.user
        return kw

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["life"] = self.cylinder_life
        return ctx

    def get_success_url(self):
        return reverse('cylinder_life_detail', kwargs={'pk': self.cylinder_life.id})

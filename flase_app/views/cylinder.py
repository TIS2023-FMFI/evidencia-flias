from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.forms import Form
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView, FormView, \
    TemplateView
from django.utils.functional import cached_property

from flase_app.forms import CylinderFilterForm, CylinderLifeUpdateForm, RelocateForm
from flase_app.mixins import OperatorRequiredMixin, EditorRequiredMixin
from flase_app.models import CylinderLife, CylinderChange
from django.views.generic.detail import DetailView
import csv
from django.http import HttpResponse, HttpResponseRedirect, Http404
from datetime import datetime, timedelta


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


def can_undo(user, change):
    # Reader cannot undo anything
    if user.role <= user.Role.READER:
        return False

    # Operators can undo any change
    if user.role >= user.Role.OPERATOR:
        return True

    # Editors can only undo their changes that were made in the last 24 hours
    if change.user != user:
        return False
    return change.timestamp <= timezone.now() - timedelta(hours=24)


class CylinderLifeDetailView(LoginRequiredMixin, DetailView):
    model = CylinderLife
    template_name = 'cylinders/detail.html'
    context_object_name = 'cylinder_life'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        first_use = CylinderChange.objects.filter(life_id=self.object.id, is_connected=True).order_by(
            'timestamp').values_list('timestamp', flat=True).first()
        context['first_use'] = first_use
        changes = CylinderChange.objects.filter(life_id=self.object.id).order_by('-timestamp').all()
        context['history'] = changes
        context['deliveries'] = CylinderLife.objects.filter(cylinder_id=self.object.cylinder.id).order_by('-start_date')

        pressure_changes = CylinderChange.objects.filter(life_id=self.object.id, pressure__isnull=False).order_by('timestamp')
        chart_data = []
        for change in pressure_changes:
            chart_data.append({"x": change.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "y": change.pressure})
        context["chart_data"] = chart_data
        context["can_undo"] = can_undo(self.request.user, changes[0])
        
        return context


class CylinderUndoChangeView(EditorRequiredMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        life = get_object_or_404(CylinderLife, id=self.kwargs["pk"])

        changes = CylinderChange.objects.filter(life=life).order_by('-timestamp')
        latest_change = changes.first()
        if not can_undo(request.user, latest_change):
            raise PermissionDenied()

        if not latest_change:
            raise PermissionDenied()

        if latest_change.pressure:
            previous_pressure_change = changes.exclude(id=latest_change.id).filter(pressure__isnull=False).first()
            if not previous_pressure_change:
                raise PermissionDenied()

            life.pressure = previous_pressure_change.pressure

        if latest_change.location:
            previous_location_change = changes.exclude(id=latest_change.id).filter(location__isnull=False).first()
            if not previous_location_change:
                raise PermissionDenied()

            life.location = previous_location_change.location
            life.is_connected = previous_location_change.is_connected

        latest_change.delete()
        life.save()

        return HttpResponseRedirect(reverse('cylinder_life_detail', kwargs={'pk': life.id}))


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


class CylinderLifeEndForm(OperatorRequiredMixin, TemplateView):
    template_name = "cylinder_life/end.html"

    @cached_property
    def life(self):
        return get_object_or_404(CylinderLife, id=self.kwargs["pk"], is_current=True)

    def post(self, request, *args, **kwargs):
        life = self.life
        life.is_current = False
        life.end_date = timezone.now()
        life.save()

        return HttpResponseRedirect(reverse('cylinder_life_detail', kwargs={'pk': self.kwargs["pk"]}))

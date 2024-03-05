import base64
import os.path
import secrets

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView, FormView, \
    TemplateView
from django.utils.functional import cached_property

from flase_app.detection import detect_pressure
from flase_app.forms import CylinderFilterForm, CylinderLifeUpdateForm, RelocateForm, \
    BarcodeForm, CylinderLifeCreateForm, PressureLogForm, AutomaticPressureLogForm
from flase_app.mixins import OperatorRequiredMixin, EditorRequiredMixin

from flase_app.models import CylinderLife, CylinderChange, Cylinder
from django.views.generic.detail import DetailView
import csv
from django.http import HttpResponse, HttpResponseRedirect
from datetime import timedelta


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

        building = form.cleaned_data.get("building")
        if building:
            qs = qs.filter(location__workplace__building=building)

        workplace = form.cleaned_data.get("workplace")
        if workplace:
            qs = qs.filter(location__workplace=workplace)

        if not form.cleaned_data.get("show_inactive"):
            qs = qs.filter(is_current=True)

        return qs

    def get_queryset(self):
        qs = CylinderLife.objects.filter(is_latest=True).select_related("cylinder", "gas", "supplier", "location",
                                                                         "location__workplace",
                                                                         "location__workplace__building",
                                                                         "cylinder__owner").order_by("cylinder__barcode")

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
        date = timezone.localtime().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"cylinders_{date}.csv"
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename=' + filename},
        )

        writer = csv.writer(response)
        writer.writerow(["barcode", "gas", "volume", "pressure", "pressure_date", "location", "is_connected", "owner", "supplier", "note"])

        for obj in self.get_queryset():
            obj: CylinderLife
            writer.writerow(list(map(str, [
                obj.cylinder.barcode,
                obj.gas or "",
                obj.volume or "",
                obj.pressure or "",
                obj.pressure_date or "",
                obj.location,
                "1" if obj.is_connected else "0",
                obj.cylinder.owner or "",
                obj.supplier or "",
                obj.note or "",
            ])))

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
        
        changes = CylinderChange.objects.select_related("user", "location", "location__workplace", "location__workplace__building").filter(life_id=self.object.id).order_by('-timestamp').all()
        context['history'] = changes
        context['deliveries'] = CylinderLife.objects.select_related("gas").filter(cylinder_id=self.object.cylinder.id).order_by('-start_date')

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
                life.pressure = None
                life.pressure_date = None
            else:
                life.pressure = previous_pressure_change.pressure
                life.pressure_date = previous_pressure_change.timestamp

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


class ScanBarcodeView(LoginRequiredMixin, FormView):
    template_name = "cylinders/scan_barcode.html"
    form_class = BarcodeForm

    def form_valid(self, form):
        cylinder_life = CylinderLife.objects.filter(cylinder__barcode=form.cleaned_data['barcode']).order_by("-start_date").first()
        if not cylinder_life:
            return render(self.request, "cylinders/scan_barcode.html", {"error": True, "barcode": form.cleaned_data['barcode']})
        return redirect("cylinder_life_detail", pk=cylinder_life.id)


class CylinderCreateView(OperatorRequiredMixin, CreateView):
    template_name = "cylinders/create.html"
    form_class = CylinderLifeCreateForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        barcode = self.request.GET.get("barcode")
        kw["cylinder"] = Cylinder.objects.filter(barcode=barcode).first()
        return kw

    def get_initial(self):
        initial = super().get_initial()
        barcode = self.request.GET.get("barcode")
        if barcode:
            initial["barcode"] = barcode
        return initial

    def get_success_url(self):
        return reverse("cylinder_list")


class PressureLogView(EditorRequiredMixin, CreateView):
    form_class = PressureLogForm
    template_name = "cylinders/log_pressure.html"

    @cached_property
    def cylinder_life(self):
        return get_object_or_404(CylinderLife, id=self.kwargs["pk"])

    def get_initial(self):
        initial = super().get_initial()
        initial["pressure"] = self.cylinder_life.pressure
        if "pressure" in self.request.GET:
            initial["pressure"] = self.request.GET["pressure"]
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
        life.pressure_date = change.timestamp
        life.save()

        return HttpResponseRedirect(reverse('cylinder_life_detail', kwargs={'pk': life.id}))


class AutomaticPressureLogView(EditorRequiredMixin, FormView):
    form_class = AutomaticPressureLogForm
    template_name = "cylinders/log_pressure_auto.html"

    @cached_property
    def cylinder_life(self):
        return get_object_or_404(CylinderLife, id=self.kwargs["pk"])

    def get_initial(self):
        initial = super().get_initial()
        if self.cylinder_life.manometer_min is not None:
            initial["min"] = self.cylinder_life.manometer_min
        if self.cylinder_life.manometer_max is not None:
            initial["max"] = self.cylinder_life.manometer_max
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["life"] = self.cylinder_life
        return ctx

    def form_valid(self, form):
        data = form.cleaned_data["image_b64"].split(";base64,", 1)[1]
        data = base64.b64decode(data)

        life = self.cylinder_life
        life.manometer_min = form.cleaned_data["min"]
        life.manometer_max = form.cleaned_data["max"]
        life.save()

        output = None
        if settings.FLASE_IMAGE_DIR:
            file_directory = settings.FLASE_IMAGE_DIR
            os.makedirs(file_directory, exist_ok=True)
            name = secrets.token_hex(16)
            file_path = os.path.join(file_directory, f"{name}.jpg")
            with open(file_path, "wb") as f:
                f.write(data)
            output = os.path.join(file_directory, f"{name}-cv.jpg")

        pressure = detect_pressure(data, form.cleaned_data["min"], form.cleaned_data["max"], output)
        return HttpResponseRedirect(reverse('cylinder_life_pressure', kwargs={'pk': self.cylinder_life.id}) + f"?pressure={pressure}")

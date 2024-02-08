from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView

from flase_app.forms import CylinderFilterForm
from flase_app.models import CylinderLife, CylinderChange
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
import csv
from django.http import HttpResponse
from datetime import datetime


class CylinderListView(LoginRequiredMixin, ListView):
    model = CylinderLife
    template_name = "cylinders/list.html"

    def search_object(self, qs, query):
        search_object = Q(note__icontains=query)
        search_object |= Q(cylinder__barcode__icontains=query)
        search_object |= Q(cylinder__owner__name__contains=query)
        search_object |= Q(supplier__name__contains=query)
        search_object |= Q(gas__name__contains=query)
        search_object |= Q(location__name__contains=query)
        qs = qs.filter(search_object)
        return qs

    def filter_objects(self, qs, query, gas, owner, volume, supplier, location, status):
        if query:
            qs = self.search_object(qs, query)
        if gas:
            qs = qs.filter(gas=gas)
        if owner:
            qs = qs.filter(cylinder__owner=owner)
        if volume:
            qs = qs.filter(volume=volume)
        if supplier:
            qs = qs.filter(supplier=supplier)
        if location:
            qs = qs.filter(location=location)
        if status:
            qs = qs.filter(is_connected=(status == "c"))
        return qs

    def post(self, *args, **kwargs):
        qs = CylinderLife.objects.filter(is_current=True).select_related("cylinder", "gas", "supplier", "location",
                                                                         "location__workplace",
                                                                         "location__workplace__building",
                                                                         "cylinder__owner")

        query = self.request.session.get('query')
        gas = self.request.session.get('gas')
        owner = self.request.session.get('owner')
        volume = self.request.session.get('volume')
        supplier = self.request.session.get('supplier')
        location = self.request.session.get('location')
        status = self.request.session.get('status')

        qs = self.filter_objects(qs, query, gas, owner, volume, supplier, location, status)
        return self.export_csv(qs)

    def get_queryset(self):
        qs = CylinderLife.objects.filter(is_current=True).select_related("cylinder", "gas", "supplier", "location",
                                                                         "location__workplace",
                                                                         "location__workplace__building",
                                                                         "cylinder__owner")

        form = CylinderFilterForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("query")

            gas = form.cleaned_data.get("gas")
            owner = form.cleaned_data.get("owner")
            volume = form.cleaned_data.get("volume")
            supplier = form.cleaned_data.get("supplier")
            location = form.cleaned_data.get("location")
            status = form.cleaned_data.get("status")

            qs = self.filter_objects(qs, query, gas, owner, volume, supplier, location, status)


            self.request.session['query'] = self.request.GET.get('query')
            self.request.session['gas'] = self.request.GET.get('gas')
            self.request.session['owner'] = self.request.GET.get('owner')
            self.request.session['volume'] = self.request.GET.get('volume')
            self.request.session['supplier'] = self.request.GET.get('supplier')
            self.request.session['location'] = self.request.GET.get('location')
            self.request.session['status'] = self.request.GET.get('status')
        return qs

    def export_csv(self, queryset):
        date = datetime.now().date()
        filename = f"export-cylinders-{date}.csv"
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename=' + filename},
        )

        writer = csv.writer(response)
        writer.writerow(
            ["Row number", "Gas", "Barcode", "Owner", "Current Location", "Volume", "Supplier", "Notes"])

        if not queryset:
            return response

        for index, obj in enumerate(queryset):
            writer.writerow([
                index,
                obj.gas.name,
                obj.cylinder.barcode,
                obj.cylinder.owner.name,
                obj.location.name,
                obj.volume,
                obj.supplier.name,
                obj.note,
            ])

        return response


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = CylinderFilterForm(self.request.GET or None)
        return context


class CylinderDetailView(DetailView):
    model = CylinderLife
    template_name = 'cylinders/detail.html'
    context_object_name = 'cylinder_life'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cylinder_life_id = self.kwargs.get('pk')
        context['history'] = CylinderChange.objects.filter(life_id=cylinder_life_id).order_by('-timestamp')
        return context


class CylinderUpdateView(UpdateView):
    model = CylinderLife
    fields = ['gas', 'volume', 'pressure', 'location', 'note']
    template_name = 'cylinders/edit.html'
    success_url = reverse_lazy('cylinder_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Cylinder Properties'
        context['cylinder_id'] = self.object.cylinder.id
        return context

    def get_success_url(self):
        cylinder_id = self.object.cylinder.id
        return reverse('cylinder_detail', kwargs={'pk': cylinder_id})
    # TODO: Spýtať sa na históriu ako je to myslené. Teda podľa čoho ju zobrazovať.

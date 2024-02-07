from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView

from flase_app.forms import CylinderFilterForm
from flase_app.models import CylinderLife, CylinderChange
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView


class CylinderListView(LoginRequiredMixin, ListView):
    model = CylinderLife
    template_name = "cylinders/list.html"

    def get_queryset(self):
        qs = CylinderLife.objects.filter(is_current=True).select_related("cylinder", "gas", "supplier", "location",
                                                                         "location__workplace",
                                                                         "location__workplace__building",
                                                                         "cylinder__owner")

        form = CylinderFilterForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("query")
            if query:
                search_object = Q(note__icontains=query)
                search_object |= Q(cylinder__barcode__icontains=query)
                search_object |= Q(cylinder__owner__name__contains=query)
                search_object |= Q(supplier__name__contains=query)
                search_object |= Q(gas__name__contains=query)
                search_object |= Q(location__name__contains=query)
                qs = qs.filter(search_object)

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

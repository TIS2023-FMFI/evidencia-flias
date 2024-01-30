from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from flase_app.forms import OwnerForm, SupplierForm, UserForm, CylinderLifeForm, \
    PressureLogForm
from flase_app.models import Owner, Supplier, CylinderLife, User, Cylinder


class OwnerListView(LoginRequiredMixin, ListView):
    model = Owner
    template_name = "owners/list.html"


class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Owner
    template_name = "owners/update.html"
    form_class = OwnerForm

    def get_success_url(self):
        return reverse("owner_list")


class OwnerCreateView(LoginRequiredMixin, CreateView):
    template_name = "owners/update.html"
    form_class = OwnerForm

    def get_success_url(self):
        return reverse("owner_list")


class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    model = Owner
    template_name = "owners/delete.html"

    def get_success_url(self):
        return reverse("owner_list")


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/list.html"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "users/update.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse("user_list")


class UserCreateView(LoginRequiredMixin, CreateView):
    template_name = "users/update.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse("user_list")


class UserDisableView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "users/disable.html"

    def get_success_url(self):
        return reverse("user_list")

      
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = "suppliers/list.html"


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/form.html"

    def get_success_url(self):
        return reverse("supplier_list")


class SupplierCreateView(LoginRequiredMixin, CreateView):
    form_class = SupplierForm
    template_name = "suppliers/form.html"

    def get_success_url(self):
        return reverse("supplier_list")


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = "suppliers/delete.html"

    def get_success_url(self):
        return reverse("supplier_list")


class CylinderLifeListView(ListView):
    model = CylinderLife
    template_name = "index.html"

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
    template_name = "cylinders/list.html"


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

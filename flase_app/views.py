from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from flase_app.forms import OwnerForm, SupplierForm, UserForm, CylinderLifeForm
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

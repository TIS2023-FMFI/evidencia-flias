from django.urls import path

from flase_app import views
from flase_app.views import CylinderLifeListView, CylinderListView
from flase_app.views.owner import OwnerListView, OwnerCreateView, OwnerUpdateView, \
    OwnerDeleteView

urlpatterns = [
    # Owners
    path("owners/", OwnerListView.as_view(), name="owner_list"),
    path("owners/create/", OwnerCreateView.as_view(), name="owner_create"),
    path("owners/<int:pk>/", OwnerUpdateView.as_view(), name="owner_update"),
    path("owners/<int:pk>/delete/", OwnerDeleteView.as_view(), name="owner_delete"),
    #
    path('cylinders/', CylinderListView.as_view(), name='cylinder_list'),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", views.UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/disable/", views.UserDisableView.as_view(), name="user_disable"),
    path("users/create/", views.UserCreateView.as_view(), name="user_create"),
    path("suppliers/", views.SupplierListView.as_view(), name="supplier_list"),
    path("suppliers/<int:pk>/", views.SupplierUpdateView.as_view(), name="supplier_update"),
    path("suppliers/<int:pk>/delete/", views.SupplierDeleteView.as_view(), name="supplier_delete"),
    path("suppliers/create/", views.SupplierCreateView.as_view(), name="supplier_create"),
    path("cylinders/", CylinderLifeListView.as_view(), name="cylinder_list"),
    path("cylinders/create", views.CylinderCreateView.as_view(), name="cylinder_create"),
    path("cylinders/<int:pk>/", views.CylinderUpdateView.as_view(), name="cylinder_update"),
    path("cylinders/life/<int:pk>/pressure/manual/", views.PressureLogView.as_view(), name="cylinder_life_pressure"),
    path("cylinders/life/<int:pk>/edit/", views.CylinderLifeUpdateView.as_view(), name="cylinder_life_update"),
]

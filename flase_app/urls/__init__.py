from django.urls import path
from flase_app import views

from flase_app.views.cylinder import CylinderListView, CylinderDetailView, CylinderUpdateView
from flase_app.views.gas import (
    GasListView,
    GasCreateView,
    GasUpdateView,
    GasDeleteView
)
from flase_app.views.owner import (
    OwnerListView,
    OwnerCreateView,
    OwnerUpdateView,
    OwnerDeleteView,
)
from flase_app.views.supplier import (
    SupplierListView,
    SupplierUpdateView,
    SupplierDeleteView,
    SupplierCreateView,
)
from flase_app.views.user import (
    UserListView,
    UserUpdateView,
    UserDisableView,
    UserCreateView,
)

urlpatterns = [
    # Owners
    path("owners/", OwnerListView.as_view(), name="owner_list"),
    path("owners/create/", OwnerCreateView.as_view(), name="owner_create"),
    path("owners/<int:pk>/", OwnerUpdateView.as_view(), name="owner_update"),
    path("owners/<int:pk>/delete/", OwnerDeleteView.as_view(), name="owner_delete"),
    # Users
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/disable/", UserDisableView.as_view(), name="user_disable"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    # Suppliers
    path("suppliers/", SupplierListView.as_view(), name="supplier_list"),
    path("suppliers/<int:pk>/", SupplierUpdateView.as_view(), name="supplier_update"),
    path(
        "suppliers/<int:pk>/delete/",
        SupplierDeleteView.as_view(),
        name="supplier_delete",
    ),
    path("suppliers/create/", SupplierCreateView.as_view(), name="supplier_create"),
    # Cylinder
    path("cylinders/", CylinderListView.as_view(), name="cylinder_list"),
    path(
        "cylinders/create", views.CylinderCreateView.as_view(), name="cylinder_create"
    ),
    path(
        "cylinders/<int:pk>/",
        views.CylinderUpdateView.as_view(),
        name="cylinder_update",
    ),
    path(
        "cylinders/life/<int:pk>/pressure/manual/",
        views.PressureLogView.as_view(),
        name="cylinder_life_pressure",
    ),
    path(
        "cylinders/life/<int:pk>/edit/",
        views.CylinderLifeUpdateView.as_view(),
        name="cylinder_life_update",
    ),
    path('cylinders/detail/<int:pk>/', CylinderDetailView.as_view(), name='cylinder_detail'),
    path('cylinders/edit/<int:pk>/', CylinderUpdateView.as_view(), name='cylinder_edit'),
    # Gas
    path('gasses/', GasListView.as_view(), name='gas_list'),
    path('gasses/new/', GasCreateView.as_view(), name='gas_new'),
    path('gasses/edit/<int:pk>/', GasUpdateView.as_view(), name='gas_edit'),
    path('gasses/delete/<int:pk>/', GasDeleteView.as_view(), name='gas_delete'),
]

from django.urls import path
from django.views.i18n import set_language

from flase_app.views import places, cylinder

from flase_app.views.gas import (
    GasListView,
    GasCreateView,
    GasUpdateView,
    GasDeleteView
)
from flase_app.views.home import HomeRedirectView
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
    path("cylinders/", cylinder.CylinderListView.as_view(), name="cylinder_list"),
    path("cylinders/export/", cylinder.CylinderExportView.as_view(), name="cylinder_export"),
    path(
        "cylinders/create/", cylinder.CylinderCreateView.as_view(), name="cylinder_create"
    ),
    path(
        "cylinders/life/<int:pk>/pressure/manual/",
        cylinder.PressureLogView.as_view(),
        name="cylinder_life_pressure",
    ),
    path(
        "cylinders/life/<int:pk>/pressure/automatic/",
        cylinder.AutomaticPressureLogView.as_view(),
        name="cylinder_life_pressure_auto",
    ),
    path(
        "cylinders/life/<int:pk>/edit/",
        cylinder.CylinderLifeUpdateView.as_view(),
        name="cylinder_life_update",
    ),
    path(
        "cylinders/life/<int:pk>/undo/",
        cylinder.CylinderUndoChangeView.as_view(),
        name="cylinder_life_undo",
    ),
    path(
        "cylinders/life/<int:pk>/relocate/",
        cylinder.CylinderLifeRelocateView.as_view(),
        name="cylinder_life_relocate",
    ),
    path('cylinders/life/<int:pk>/', cylinder.CylinderLifeDetailView.as_view(), name='cylinder_life_detail'),
    path('cylinders/life/<int:pk>/end/', cylinder.CylinderLifeEndForm.as_view(), name='cylinder_life_end'),
    path('cylinders/scan/', cylinder.ScanBarcodeView.as_view(), name='cylinder_scan_barcode'),
    # Gas
    path('gasses/', GasListView.as_view(), name='gas_list'),
    path('gasses/new/', GasCreateView.as_view(), name='gas_new'),
    path('gasses/edit/<int:pk>/', GasUpdateView.as_view(), name='gas_edit'),
    path('gasses/delete/<int:pk>/', GasDeleteView.as_view(), name='gas_delete'),
    # Places
    path("places/workplaces/", places.WorkplaceListView.as_view(), name="workplace_list"),
    path("places/workplaces/create/", places.WorkplaceCreateView.as_view(), name="workplace_create"),
    path("places/workplaces/<int:pk>/", places.WorkplaceUpdateView.as_view(), name="workplace_update"),
    path("places/workplaces/<int:pk>/delete/", places.WorkplaceDeleteView.as_view(), name="workplace_delete"),
    path("places/buildings/", places.BuildingListView.as_view(), name="building_list"),
    path("places/buildings/create/", places.BuildingCreateView.as_view(), name="building_create"),
    path("places/buildings/<int:pk>/", places.BuildingUpdateView.as_view(), name="building_update"),
    path("places/buildings/<int:pk>/delete/", places.BuildingDeleteView.as_view(), name="building_delete"),
    path("places/locations/", places.LocationListView.as_view(), name="location_list"),
    path("places/locations/create/", places.LocationCreateView.as_view(), name="location_create"),
    path("places/locations/<int:pk>/", places.LocationUpdateView.as_view(), name="location_update"),
    path("places/locations/<int:pk>/delete/", places.LocationDeleteView.as_view(), name="location_delete"),
    # Redirect
    path('', HomeRedirectView.as_view(), name='home'),
    path("set_language/", set_language, name="set_language"),
]

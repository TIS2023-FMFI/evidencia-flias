from django.urls import path
from . import views
from flase_app.views import CylinderLifeListView

urlpatterns = [
    path("owners/", views.OwnerListView.as_view(), name="owner_list"),
    path("owners/<int:pk>/", views.OwnerUpdateView.as_view(), name="owner_update"),
    path("owners/<int:pk>/delete/", views.OwnerDeleteView.as_view(), name="owner_delete"),
    path("owners/create/", views.OwnerCreateView.as_view(), name="owner_create"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", views.UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/disable/", views.UserDisableView.as_view(), name="user_disable"),
    path("users/create/", views.UserCreateView.as_view(), name="user_create"),
    path("suppliers/", views.SupplierListView.as_view(), name="supplier_list"),
    path("suppliers/<int:pk>/", views.SupplierUpdateView.as_view(), name="supplier_update"),
    path("suppliers/<int:pk>/delete/", views.SupplierDeleteView.as_view(), name="supplier_delete"),
    path("suppliers/create/", views.SupplierCreateView.as_view(), name="supplier_create"),
    path("cylinders/", CylinderLifeListView.as_view(), name="cylinder_list"),
]

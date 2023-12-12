from django.urls import path
from . import views

urlpatterns = [
    path("owners/", views.OwnerListView.as_view(), name="owner_list"),
    path("owners/<int:pk>/", views.OwnerUpdateView.as_view(), name="owner_update"),
    path("owners/<int:pk>/delete/", views.OwnerDeleteView.as_view(), name="owner_delete"),
    path("owners/create/", views.OwnerCreateView.as_view(), name="owner_create"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", views.UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/disable/", views.UserDisableView.as_view(), name="user_disable"),
    path("users/create/", views.UserCreateView.as_view(), name="user_create"),
]
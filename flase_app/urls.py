from django.urls import path
from .views import ZoznamPlynovView, PridatPlynView, UpravitPlynView, VymazatPlynView

urlpatterns = [
    path('plynov/', ZoznamPlynovView.as_view(), name='zoznam_plynov'),
    path('pridat/', PridatPlynView.as_view(), name='pridat_plyn'),
    path('upravit/<int:pk>/', UpravitPlynView.as_view(), name='upravit_plyn'),
    path('vymazat/<int:pk>/', VymazatPlynView.as_view(), name='vymazat_plyn'),
]

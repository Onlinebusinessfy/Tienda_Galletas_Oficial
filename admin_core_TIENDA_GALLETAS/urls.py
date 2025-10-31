from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('formulario/', formulario, name='formulario'),
    path('about/', about, name='about'),
    path('galleta/', galleta, name='galleta'),
    path('galleta_create/', galleta_create, name='galleta_create'),
    path('orden/', orden, name='orden'),
    path('venta/', venta, name='venta'),
    path('detalle_venta/', detalle_venta, name='detalle_venta'),
]
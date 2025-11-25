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
    path('carrito/', carrito, name='carrito'),
    path('carrito/agregar/<int:galleta_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_id>/', actualizar_cantidad, name='actualizar_cantidad'),
    path('pago/', pago, name='pago'),
    path('procesar-pago/', procesar_pago, name='procesar_pago'),
]


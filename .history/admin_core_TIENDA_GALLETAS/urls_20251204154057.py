from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('formulario/', views.formulario, name='formulario'),
    path('about/', views.about, name='about'),
    path('galleta/', views.galleta_view, name='galleta'),  # ¡Cambiado a galleta_view!
    path('galleta_create/', views.galleta_create, name='galleta_create'),
    path('orden/', views.orden, name='orden'),
    path('venta/', views.venta, name='venta'),
    path('detalle_venta/', views.detalle_venta, name='detalle_venta'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:galleta_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('pago/', views.pago, name='pago'),
    path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('contacto/', views.formulario_contacto, name='formulario'),
    path('contacto/webhook/', views.contacto_webhook, name='contacto_webhook'),
    
    # NUEVAS URLs PARA STRIPE Y OXXO
    path('seleccionar-pago/', views.seleccionar_metodo_pago, name='seleccionar_pago'),
    path('pago-stripe/', views.pago_stripe, name='pago_stripe'),  # ¡NUEVA!
    path('pago-oxxo/', views.pago_oxxo, name='pago_oxxo'),  # ¡NUEVA!
    path('recibo/', views.recibo, name='recibo'),  # ¡NUEVA!
    path('pago-stripe/webhook/', views.pago_stripe_webhook, name='stripe_webhook'),
    path('verificar-pago/<int:orden_id>/', views.verificar_pago, name='verificar_pago'),
    path('historial-pedidos/', views.historial_pedidos, name='historial_pedidos'),

]
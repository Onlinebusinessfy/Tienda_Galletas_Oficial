from django.contrib import admin
from .models import *
# Register your models here. 

admin.site.register(Galleta)
admin.site.register(Cliente)
admin.site.register(Orden)
admin.site.register(Pago)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
# admin_core_TIENDA_GALLETAS/admin.py
from django.contrib import admin

# 1. Primero, NO importes nada de models

# 2. Define clases Admin vacías que se llenarán después
class ClienteAdmin(admin.ModelAdmin):
    pass

class GalletaAdmin(admin.ModelAdmin):
    pass

class OrdenAdmin(admin.ModelAdmin):
    pass

class PagoAdmin(admin.ModelAdmin):
    pass

class VentaAdmin(admin.ModelAdmin):
    pass

class DetalleVentaAdmin(admin.ModelAdmin):
    pass

class CarritoAdmin(admin.ModelAdmin):
    pass

class CarritoItemAdmin(admin.ModelAdmin):
    pass

class ItemCarritoAdmin(admin.ModelAdmin):
    pass

# 3. Ahora intenta importar y registrar
try:
    # Intenta importar
    import sys
    import importlib
    
    # Fuerza recarga del módulo models si ya estaba cargado
    module_name = 'admin_core_TIENDA_GALLETAS.models'
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    
    from . import models
    
    # Registra usando las clases Admin definidas
    admin.site.register(models.Cliente, ClienteAdmin)
    admin.site.register(models.Galleta, GalletaAdmin)
    admin.site.register(models.Orden, OrdenAdmin)
    admin.site.register(models.Pago, PagoAdmin)
    admin.site.register(models.Venta, VentaAdmin)
    admin.site.register(models.DetalleVenta, DetalleVentaAdmin)
    admin.site.register(models.Carrito, CarritoAdmin)
    admin.site.register(models.CarritoItem, CarritoItemAdmin)
    admin.site.register(models.ItemCarrito, ItemCarritoAdmin)
    
    print("=" * 50)
    print("✅ ADMIN CONFIGURADO CORRECTAMENTE")
    print("=" * 50)
    
except Exception as e:
    print("=" * 50)
    print(f"❌ ERROR: {e}")
    print("=" * 50)
    # No hagas nada más, deja que Django continúe
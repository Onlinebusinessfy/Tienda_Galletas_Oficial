# admin_core_TIENDA_GALLETAS/admin.py
from django.contrib import admin
from .models import ContactMessage

# Solo importa los modelos que necesitas
try:
    from .models import (
        Cliente, Galleta, Orden, Pago, Venta,
        DetalleVenta, Carrito, CarritoItem, ItemCarrito
    )
    
    # Registro básico
    admin.site.register(Cliente)
    admin.site.register(Galleta)
    admin.site.register(Orden)
    admin.site.register(Pago)
    admin.site.register(Venta)
    admin.site.register(DetalleVenta)
    admin.site.register(Carrito)
    admin.site.register(CarritoItem)
    admin.site.register(ItemCarrito)
    
except ImportError:
    # Si falla, no hagas nada
    pass

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'asunto', 'leido', 'respondido', 'created_at')
    list_filter = ('leido', 'respondido', 'newsletter', 'created_at')
    search_fields = ('nombre', 'email', 'asunto', 'mensaje')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información del Contacto', {
            'fields': ('nombre', 'email', 'asunto', 'mensaje', 'newsletter')
        }),
        ('Estado', {
            'fields': ('leido', 'respondido')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
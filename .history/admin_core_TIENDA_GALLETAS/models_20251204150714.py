# admin_core_TIENDA_GALLETAS/admin.py
from django.contrib import admin
from .models import Cliente, Galleta, Orden, Pago, ItemCarrito, Venta, DetalleVenta, Carrito, CarritoItem

# Registro básico para todos los modelos
admin.site.register(Cliente)
admin.site.register(Galleta)

# Configuración para Orden con ItemCarrito inline
class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ['subtotal']

    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = 'Subtotal'

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'total', 'metodo_pago', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'metodo_pago', 'fecha_creacion']
    search_fields = ['usuario__username', 'id', 'oxxo_referencia']
    readonly_fields = ['fecha_creacion']
    inlines = [ItemCarritoInline]

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['id', 'pedido', 'direccion_envio', 'fecha_envio', 'estado']
    list_filter = ['estado', 'fecha_envio']
    search_fields = ['pedido__id', 'direccion_envio']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id_venta', 'cliente', 'precio_total', 'metodo_pago', 'fecha_hora_venta']
    list_filter = ['metodo_pago', 'fecha_hora_venta']
    search_fields = ['id_venta', 'cliente__nombre']

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['id_detalle_venta', 'venta', 'galleta', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['venta']

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'fecha_creacion', 'total']
    search_fields = ['usuario__username']

class CarritoItemInline(admin.TabularInline):
    model = CarritoItem
    extra = 0
    readonly_fields = ['subtotal']

    def subtotal(self, obj):
        return obj.subtotal

@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'carrito', 'galleta', 'cantidad', 'subtotal']
    list_filter = ['carrito__usuario']
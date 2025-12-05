from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.IntegerField()
    email = models.EmailField(unique=True)
    Direccion = models.CharField(max_length=500)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

class Galleta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    precio = models.FloatField()
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to='galletas/', null=True, blank=True)
    
    def __str__(self):
        return self.nombre

class Orden(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateField()
    total = models.FloatField()
    
    def __str__(self):
        return f"Orden #{self.id} - {self.cliente.nombre}"

class Pago(models.Model):
    ESTADO_CHOICES = [
        ("PAGADO", "Pagado"),
        ("NO_PAGADO", "No pagado"),
        ("EN_PROCESO", "En proceso"),
    ]
    
    pedido = models.ForeignKey(Orden, on_delete=models.CASCADE)
    direccion_envio = models.CharField(max_length=100)
    fecha_envio = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="EN_PROCESO")

    def __str__(self):
        return f"Pago Orden #{self.pedido.id} - {self.estado}"

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_hora_venta = models.DateTimeField(auto_now_add=True)
    precio_total = models.FloatField()
    metodo_pago = models.CharField(max_length=50)

    def __str__(self):
        return f"Venta #{self.id_venta} - Total: {self.precio_total}"

class DetalleVenta(models.Model):
    id_detalle_venta = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    galleta = models.ForeignKey(Galleta, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.FloatField()
    subtotal = models.FloatField()

    def __str__(self):
        return f"Detalle {self.id_detalle_venta} - {self.galleta.nombre} ({self.cantidad})"

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    galleta = models.ForeignKey(Galleta, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cantidad} x {self.galleta.nombre}"

    @property
    def subtotal(self):
        return self.galleta.precio * self.cantidad
    


class Orden(models.Model):
    METODO_PAGO_CHOICES = [
        ('stripe', 'Tarjeta (Stripe)'),
        ('oxxo', 'Efectivo (OXXO)'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de pago'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Campos para Stripe
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_client_secret = models.CharField(max_length=200, blank=True, null=True)
    
    # Campos para OXXO
    oxxo_referencia = models.CharField(max_length=50, blank=True, null=True)
    oxxo_caducidad = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username}"

class ItemCarrito(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    nombre_producto = models.CharField(max_length=200)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    def subtotal(self):
        return self.cantidad * self.precio
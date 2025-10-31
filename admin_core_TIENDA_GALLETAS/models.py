from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.IntegerField()
    email = models.EmailField(unique=True)
    Direccion = models.CharField(max_length=500)
    fecha_registro = models.DateTimeField(auto_now_add=True)

class Galleta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    precio = models.FloatField()
    stock = models.IntegerField()
    
class Orden(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateField()
    total = models.FloatField()
    def __str__(self):
        return f"Orden #{self.id} - {self.cliente.nombre}"
    
class Pago(models.Model):
    pedido = models.ForeignKey(Orden, on_delete=models.CASCADE)
    direccion_envio = models.CharField(max_length=100)
    fecha_envio = models.DateField()
    estado = [
        ("PAGADO", "Pagado"),
        ("NO_PAGADO", "No pagado"),
        ("EN_PROCESO", "En proceso"),
    ]

    def __str__(self):
       return f"{self.estado}"

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    fecha_hora_venta = models.DateTimeField(auto_now_add=True)
    precio_total = models.FloatField()
    metodo_pago = models.CharField(max_length=50)

    def _str_(self):
        return f"Venta #{self.id_venta} - Total: {self.precio_total}"

class DetalleVenta(models.Model):
    id_detalle_venta = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    galleta = models.ForeignKey('Galleta', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.FloatField()
    subtotal = models.FloatField()

    def _str_(self):
        return f"Detalle {self.id_detalle_venta} - {self.galleta.nombre} ({self.cantidad})"
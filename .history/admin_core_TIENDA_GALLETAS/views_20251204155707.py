# admin_core_TIENDA_GALLETAS/views.py - VERSIÓN FINAL CORREGIDA
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt  # ← IMPORTACIÓN AÑADIDA

# ============ MANEJO SEGURO DE IMPORTACIONES ============
try:
    from .models import Galleta
    MODELO_GALLETA_DISPONIBLE = True
except ImportError:
    MODELO_GALLETA_DISPONIBLE = False
    class Galleta:
        objects = type('Manager', (), {'all': lambda self: []})()

try:
    from .models import Carrito, CarritoItem
    MODELO_CARRITO_DISPONIBLE = True
except ImportError:
    MODELO_CARRITO_DISPONIBLE = False
    class Carrito:
        objects = type('Manager', (), {'get': lambda self, **kwargs: None, 'DoesNotExist': Exception})()
    class CarritoItem:
        objects = type('Manager', (), {'all': lambda self: []})()

try:
    from .models import Orden, ItemCarrito
    MODELO_ORDEN_DISPONIBLE = True
except ImportError:
    MODELO_ORDEN_DISPONIBLE = False
    class Orden:
        objects = type('Manager', (), {
            'create': lambda self, **kwargs: type('obj', (), kwargs)(),
            'get': lambda self, **kwargs: None,
            'filter': lambda self, **kwargs: [],
            'DoesNotExist': Exception
        })()
    class ItemCarrito:
        objects = type('Manager', (), {'create': lambda self, **kwargs: None})()

try:
    from .forms import MetodoPagoForm
    FORM_PAGO_DISPONIBLE = True
except ImportError:
    FORM_PAGO_DISPONIBLE = False
    MetodoPagoForm = None

try:
    from .pagos import ProcesadorPagos
    PROCESADOR_PAGOS_DISPONIBLE = True
except ImportError:
    PROCESADOR_PAGOS_DISPONIBLE = False
    ProcesadorPagos = None

# ============ VISTAS PRINCIPALES ============

def home(request):
    return render(request, 'home.html')

@login_required
def formulario(request):
    return render(request, 'formulario.html')

def about(request):
    return render(request, 'about.html')

@login_required
def galleta_view(request):
    """Muestra todas las galletas disponibles"""
    if MODELO_GALLETA_DISPONIBLE:
        galletas = Galleta.objects.all()
    else:
        galletas = [
            type('obj', (), {
                'id': 1, 'nombre': 'Galleta de Chocolate', 'precio': 18.00,
                'descripcion': 'Deliciosa galleta con chispas de chocolate',
                'stock': 50, 'imagen': None
            }),
            type('obj', (), {
                'id': 2, 'nombre': 'Galleta de Vainilla', 'precio': 15.00,
                'descripcion': 'Galleta suave con esencia de vainilla',
                'stock': 30, 'imagen': None
            }),
        ]
    
    carrito_session = request.session.get('carrito', {})
    cart_count = sum(item.get('cantidad', 0) for item in carrito_session.values())
    
    context = {
        'galletas': galletas,
        'cart_count': cart_count
    }
    return render(request, 'galleta.html', context)

@login_required
def galleta_create(request):
    return render(request, "galleta_create.html")

@login_required
def orden(request):
    return render(request, 'orden.html')

@login_required
def venta(request):
    return render(request, 'venta.html')

@login_required
def detalle_venta(request):
    return render(request, 'detalle_venta.html')

# ============ CARRITO ============

def carrito(request):
    carrito_session = request.session.get('carrito', {})
    cart_items = []
    
    for galleta_id, item_data in carrito_session.items():
        cart_items.append({
            'id': galleta_id,
            'galleta': {
                'id': galleta_id,
                'nombre': item_data.get('nombre', f'Galleta {galleta_id}'),
                'precio': Decimal(str(item_data.get('precio', '15.00'))),
                'stock': 50,
            },
            'cantidad': item_data['cantidad'],
            'subtotal': Decimal(str(item_data.get('precio', '15.00'))) * item_data['cantidad']
        })
    
    cart_count = sum(item['cantidad'] for item in cart_items)
    subtotal = sum(item['subtotal'] for item in cart_items)
    envio = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
    total = subtotal + envio

    context = {
        'cart_items': cart_items,
        'cart_count': cart_count,
        'subtotal': subtotal,
        'envio': envio,
        'total': total
    }
    
    return render(request, 'carrito.html', context)

def agregar_al_carrito(request, galleta_id):
    if request.method == 'POST':
        carrito_session = request.session.get('carrito', {})
        galleta_str = str(galleta_id)
        
        galleta_data = {
            '1': {'nombre': 'Galleta de Chocolate', 'precio': '18.00'},
            '2': {'nombre': 'Galleta de Vainilla', 'precio': '15.00'},
        }
        
        cantidad = int(request.POST.get('cantidad', 1))
        
        if galleta_str in carrito_session:
            carrito_session[galleta_str]['cantidad'] += cantidad
        else:
            carrito_session[galleta_str] = {
                'cantidad': cantidad,
                'nombre': galleta_data.get(galleta_str, {}).get('nombre', f'Galleta {galleta_id}'),
                'precio': galleta_data.get(galleta_str, {}).get('precio', '15.00')
            }
        
        request.session['carrito'] = carrito_session
        request.session.modified = True
        
        messages.success(request, f'¡{carrito_session[galleta_str]["nombre"]} agregado al carrito!')
        return redirect('carrito')
    
    return redirect('galleta')

def eliminar_del_carrito(request, item_id):
    carrito_session = request.session.get('carrito', {})
    item_str = str(item_id)
    
    if item_str in carrito_session:
        del carrito_session[item_str]
        request.session['carrito'] = carrito_session
        request.session.modified = True
        messages.success(request, 'Producto eliminado del carrito')
    
    return redirect('carrito')

def actualizar_cantidad(request, item_id):
    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        
        if nueva_cantidad < 1:
            return JsonResponse({'error': 'La cantidad debe ser al menos 1'}, status=400)
        
        carrito_session = request.session.get('carrito', {})
        item_str = str(item_id)
        
        if item_str in carrito_session:
            carrito_session[item_str]['cantidad'] = nueva_cantidad
            request.session['carrito'] = carrito_session
            request.session.modified = True
            
            subtotal = Decimal('0.00')
            for item_data in carrito_session.values():
                subtotal += Decimal(str(item_data.get('precio', '0'))) * item_data['cantidad']
            
            envio = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
            total = subtotal + envio
            
            return JsonResponse({
                'success': True,
                'subtotal_total': float(subtotal),
                'envio': float(envio),
                'total': float(total),
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# ============ PAGOS ============

def pago(request):
    carrito_session = request.session.get('carrito', {})
    cart_count = sum(item.get('cantidad', 0) for item in carrito_session.values())
    
    subtotal = Decimal('0.00')
    for item_data in carrito_session.values():
        precio = Decimal(str(item_data.get('precio', '0.00')))
        cantidad = item_data.get('cantidad', 0)
        subtotal += precio * cantidad
    
    envio = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
    total = subtotal + envio

    context = {
        'cart_count': cart_count,
        'subtotal': subtotal,
        'envio': envio,
        'total': total
    }
    return render(request, 'pago.html', context)

def procesar_pago(request):
    if request.method == 'POST':
        messages.success(request, '🎉 ¡Pedido realizado con éxito!')
        
        if 'carrito' in request.session:
            del request.session['carrito']
            request.session.modified = True
        
        return redirect('home')
    
    return redirect('pago')

@login_required
def seleccionar_metodo_pago(request):
    carrito_session = request.session.get('carrito', {})
    
    if not carrito_session:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('carrito')
    
    subtotal = Decimal('0.00')
    for item_data in carrito_session.values():
        precio = Decimal(str(item_data.get('precio', '0.00')))
        cantidad = item_data.get('cantidad', 0)
        subtotal += precio * cantidad
    
    envio = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
    total = subtotal + envio
    
    if FORM_PAGO_DISPONIBLE:
        if request.method == 'POST':
            form = MetodoPagoForm(request.POST)
            if form.is_valid():
                metodo_pago = form.cleaned_data['metodo_pago']
                
                if metodo_pago == 'stripe':
                    return render(request, 'pago_stripe.html', {
                        'orden': {'id': 999, 'total': total},
                        'client_secret': 'demo_secret',
                        'stripe_public_key': 'demo_key'
                    })
                else:
                    return render(request, 'pago_oxxo.html', {
                        'orden': {'id': 999, 'total': total},
                        'referencia': '12345678901234',
                        'caducidad': '2024-12-31 23:59',
                        'monto': f'{total:.2f}'
                    })
        else:
            form = MetodoPagoForm()
    else:
        form = None
    
    context = {
        'form': form,
        'subtotal': subtotal,
        'envio': envio,
        'total': total,
    }
    return render(request, 'seleccionar_pago.html', context)

@login_required
def pago_stripe(request):
    return render(request, 'pago_stripe.html')

@login_required
def pago_oxxo(request):
    return render(request, 'pago_oxxo.html')

@login_required
def recibo(request):
    return render(request, 'recibo.html')

@login_required
def verificar_pago(request, orden_id):
    orden_demo = type('obj', (), {
        'id': orden_id,
        'usuario': request.user,
        'metodo_pago': 'stripe',
        'estado': 'completado',
        'total': Decimal('150.00'),
        'fecha_creacion': '2024-01-01 12:00:00',
        'get_metodo_pago_display': lambda: 'Tarjeta (Stripe)',
        'get_estado_display': lambda: 'Completado'
    })()
    
    recibo_demo = {
        'numero_orden': orden_id,
        'fecha': '01/01/2024 12:00',
        'cliente': request.user.username,
        'email': request.user.email,
        'total': '$150.00',
        'metodo_pago': 'Tarjeta (Stripe)',
        'estado': 'Completado'
    }
    
    return render(request, 'recibo.html', {
        'orden': orden_demo,
        'recibo': recibo_demo
    })

@login_required
def historial_pedidos(request):
    ordenes_demo = [
        type('obj', (), {
            'id': 1,
            'total': Decimal('150.00'),
            'metodo_pago': 'stripe',
            'estado': 'completado',
            'fecha_creacion': '2024-01-01 12:00:00',
            'get_metodo_pago_display': lambda: 'Tarjeta (Stripe)',
            'get_estado_display': lambda: 'Completado',
        }),
    ]
    
    return render(request, 'historial_pedidos.html', {
        'ordenes': ordenes_demo,
        'total_orders': 1,
        'completed_orders': 1,
        'total_spent': Decimal('150.00')
    })

# ============ WEBHOOK PARA STRIPE ============

@csrf_exempt  # ← ESTO ES LO QUE FALTABA IMPORTAR
def pago_stripe_webhook(request):
    """Webhook para recibir notificaciones de Stripe"""
    try:
        # En producción, aquí procesarías el webhook real
        return JsonResponse({'status': 'success', 'message': 'Webhook recibido'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# ============ MANEJADORES DE ERROR ============

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
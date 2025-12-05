from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Galleta, Carrito, CarritoItem
from decimal import Decimal


# Create your views here.

def home(request):
    return render(request, 'home.html')

@login_required
def formulario(request):
    return render(request, 'formulario.html')

def about(request):
    return render(request, 'about.html')

@login_required
def galleta(request):
    return render(request, 'galleta.html')

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

def carrito(request):
    carrito_session = request.session.get('carrito', {})
    cart_items = []
    
    for galleta_id, item_data in carrito_session.items():
        cart_items.append({
            'id': galleta_id,
            'galleta': {
                'id': galleta_id,
                'nombre': item_data.get('nombre', f'Galleta {galleta_id}'),
                'precio': Decimal(item_data.get('precio', '15.00')),
                'stock': 50,
                'descripcion': 'Deliciosa galleta artesanal',
            },
            'cantidad': item_data['cantidad'],
            'subtotal': Decimal(item_data.get('precio', '15.00')) * item_data['cantidad']
        })
    
    cart_count = sum(item['cantidad'] for item in cart_items)
    subtotal = sum(item['subtotal'] for item in cart_items)
    envio = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
    descuento = Decimal('0.00')
    total = subtotal + envio - descuento

    context = {
        'cart_items': cart_items,
        'cart_count': cart_count,
        'subtotal': subtotal,
        'envio': envio,
        'descuento': descuento,
        'total': total
    }
    
    return render(request, 'carrito.html', context)

def agregar_al_carrito(request, galleta_id):
    if request.method == 'POST':
        carrito_session = request.session.get('carrito', {})
        galleta_str = str(galleta_id)
        
        # Datos de ejemplo para las galletas
        galleta_data = {
            '1': {'nombre': 'Galleta de Chocolate', 'precio': '18.00'},
            '2': {'nombre': 'Galleta de Vainilla', 'precio': '15.00'},
            '3': {'nombre': 'Galleta de Avena', 'precio': '12.00'},
            '4': {'nombre': 'Galleta de Mantequilla', 'precio': '16.00'},
            '5': {'nombre': 'Galleta de Chispas', 'precio': '20.00'},
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
        messages.success(request, f'¡{carrito_session[galleta_str]["nombre"]} agregado al carrito!')
        
        return redirect('carrito')
    
    return redirect('galleta')

def eliminar_del_carrito(request, item_id):
    carrito_session = request.session.get('carrito', {})
    item_str = str(item_id)
    
    if item_str in carrito_session:
        nombre_galleta = carrito_session[item_str]['nombre']
        del carrito_session[item_str]
        request.session['carrito'] = carrito_session
        messages.success(request, f'{nombre_galleta} eliminado del carrito')
    
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
            
            # Recalcular totales
            subtotal = Decimal('0.00')
            for item_data in carrito_session.values():
                subtotal += Decimal(item_data.get('precio', '0')) * item_data['cantidad']
            
            envio = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
            total = subtotal + envio
            
            return JsonResponse({
                'success': True,
                'subtotal_total': float(subtotal),
                'envio': float(envio),
                'total': float(total)
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# CONTEXT PROCESSOR
def carrito_context(request):
    cart_count = 0
    carrito_session = request.session.get('carrito', {})
    cart_count = sum(item['cantidad'] for item in carrito_session.values())
    return {'cart_count': cart_count}

def pago(request):
    context = {
        'ordenes' : [] 
    }
    return render (request, 'pago.html', context)

def galleta(request):
    galletas = Galleta.objects.all()
    context = {
        'galletas': galletas,
        'cart_count': request.cart_count if hasattr(request, 'cart_count') else 0
    }
    return render(request, 'galleta.html', context)

def pago(request):
    # Obtener items del carrito para el resumen
    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            cart_items = carrito.items.all()
            cart_count = sum(item.cantidad for item in cart_items)
            
            # Calcular totales
            subtotal = sum(item.subtotal for item in cart_items)
            envio = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
            descuento = Decimal('0.00')
            total = subtotal + envio - descuento
            
        except Carrito.DoesNotExist:
            cart_items = []
            subtotal = Decimal('0.00')
            envio = Decimal('0.00')
            descuento = Decimal('0.00')
            total = Decimal('0.00')
    else:
        cart_items = []
        subtotal = Decimal('0.00')
        envio = Decimal('0.00')
        descuento = Decimal('0.00')
        total = Decimal('0.00')

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'envio': envio,
        'descuento': descuento,
        'total': total,
        'cart_count': cart_count
    }
    return render(request, 'pago.html', context)

def pago(request):
    # Versión simple sin modelos complejos
    cart_items = []
    subtotal = Decimal('0.00')
    envio = Decimal('50.00')
    total = Decimal('50.00')
    cart_count = 0

    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            cart_items = carrito.items.all()
            cart_count = sum(item.cantidad for item in cart_items)
            subtotal = sum(item.subtotal for item in cart_items)
            total = subtotal + envio
        except Carrito.DoesNotExist:
            pass

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'envio': envio,
        'descuento': Decimal('0.00'),
        'total': total,
        'cart_count': cart_count
    }
    return render(request, 'pago.html', context)

def procesar_pago(request):
    if request.method == 'POST':
        # Simulación de pago exitoso
        messages.success(request, '🎉 ¡Pedido realizado con éxito! Te contactaremos pronto para confirmar.')
        
        # Limpiar carrito
        if request.user.is_authenticated:
            try:
                carrito = Carrito.objects.get(usuario=request.user)
                carrito.items.all().delete()
            except Carrito.DoesNotExist:
                pass
        
        return redirect('home')
    
    return redirect('pago')


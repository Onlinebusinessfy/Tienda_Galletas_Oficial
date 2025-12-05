# admin_core_TIENDA_GALLETAS/views.py - Versión CORREGIDA
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from django.conf import settings
import json

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
def galleta_view(request):  # Cambié el nombre para evitar conflicto
    """Muestra todas las galletas disponibles"""
    # Versión segura que funciona con o sin modelos
    if MODELO_GALLETA_DISPONIBLE:
        galletas = Galleta.objects.all()
    else:
        # Datos de ejemplo para desarrollo
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
            type('obj', (), {
                'id': 3, 'nombre': 'Galleta de Avena', 'precio': 12.00,
                'descripcion': 'Galleta saludable con avena y pasas',
                'stock': 40, 'imagen': None
            }),
        ]
    
    # Obtener contador del carrito de sesión
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

# ============ CARRITO (USANDO SESIÓN) ============

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
                'descripcion': 'Deliciosa galleta artesanal',
            },
            'cantidad': item_data['cantidad'],
            'subtotal': Decimal(str(item_data.get('precio', '15.00'))) * item_data['cantidad']
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
        request.session.modified = True
        
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
        request.session.modified = True
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
            request.session.modified = True
            
            # Recalcular totales
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
                'nueva_cantidad': nueva_cantidad
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# CONTEXT PROCESSOR para el carrito
def carrito_context(request):
    carrito_session = request.session.get('carrito', {})
    cart_count = sum(item.get('cantidad', 0) for item in carrito_session.values())
    return {'cart_count': cart_count}

# ============ PAGOS ============

def pago(request):
    # Versión que funciona con o sin modelos
    cart_items = []
    subtotal = Decimal('0.00')
    envio = Decimal('50.00')
    total = Decimal('50.00')
    cart_count = 0

    # Usar sesión en lugar de modelos
    carrito_session = request.session.get('carrito', {})
    cart_count = sum(item.get('cantidad', 0) for item in carrito_session.values())
    
    # Calcular desde sesión
    for item_data in carrito_session.values():
        precio = Decimal(str(item_data.get('precio', '0.00')))
        cantidad = item_data.get('cantidad', 0)
        cart_items.append({
            'galleta': {'nombre': item_data.get('nombre', 'Galleta')},
            'cantidad': cantidad,
            'subtotal': precio * cantidad
        })
        subtotal += precio * cantidad
    
    total = subtotal + envio

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
        
        # Limpiar carrito de sesión
        if 'carrito' in request.session:
            del request.session['carrito']
            request.session.modified = True
        
        # También limpiar carrito de base de datos si existe
        if MODELO_CARRITO_DISPONIBLE and request.user.is_authenticated:
            try:
                carrito = Carrito.objects.get(usuario=request.user)
                carrito.items.all().delete()
            except:
                pass
        
        return redirect('home')
    
    return redirect('pago')

# ============ PAGOS STRIPE Y OXXO ============

@login_required
def seleccionar_metodo_pago(request):
    # Obtener carrito de la sesión
    carrito_session = request.session.get('carrito', {})
    
    if not carrito_session:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('carrito')
    
    # Verificar que el formulario esté disponible
    if not FORM_PAGO_DISPONIBLE:
        messages.error(request, 'Sistema de pagos no disponible temporalmente')
        return redirect('pago')
    
    # Calcular total desde sesión
    subtotal = Decimal('0.00')
    for item_data in carrito_session.values():
        precio = Decimal(str(item_data.get('precio', '0.00')))
        cantidad = item_data.get('cantidad', 0)
        subtotal += precio * cantidad
    
    envio = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
    total = subtotal + envio
    
    if request.method == 'POST':
        form = MetodoPagoForm(request.POST)
        if form.is_valid():
            metodo_pago = form.cleaned_data['metodo_pago']
            
            # Si los modelos no están disponibles, redirigir a simulación
            if not MODELO_ORDEN_DISPONIBLE:
                messages.info(request, 'Sistema en modo demostración')
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
            
            # Crear orden en base de datos
            try:
                orden = Orden.objects.create(
                    usuario=request.user,
                    total=total,
                    metodo_pago=metodo_pago,
                    estado='pendiente'
                )
                
                # Guardar items del carrito en la orden
                for galleta_id, item_data in carrito_session.items():
                    ItemCarrito.objects.create(
                        orden=orden,
                        nombre_producto=item_data['nombre'],
                        cantidad=item_data['cantidad'],
                        precio=Decimal(str(item_data['precio']))
                    )
                
                # Procesar según método
                if metodo_pago == 'stripe':
                    if PROCESADOR_PAGOS_DISPONIBLE:
                        resultado = ProcesadorPagos.procesar_pago(orden, 'stripe')
                        if resultado:
                            orden.stripe_payment_intent_id = resultado.get('payment_intent_id')
                            orden.stripe_client_secret = resultado.get('client_secret')
                            orden.save()
                            
                            return render(request, 'pago_stripe.html', {
                                'orden': orden,
                                'client_secret': resultado['client_secret'],
                                'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', 'demo_key')
                            })
                    # Fallback a demo
                    return render(request, 'pago_stripe.html', {
                        'orden': orden,
                        'client_secret': 'demo_client_secret_xyz',
                        'stripe_public_key': 'pk_test_demo'
                    })
                
                elif metodo_pago == 'oxxo':
                    if PROCESADOR_PAGOS_DISPONIBLE:
                        resultado = ProcesadorPagos.procesar_pago(orden, 'oxxo')
                        if resultado:
                            orden.oxxo_referencia = resultado['referencia']
                            orden.save()
                            
                            return render(request, 'pago_oxxo.html', {
                                'orden': orden,
                                'referencia': resultado['referencia'],
                                'caducidad': resultado['caducidad'],
                                'monto': resultado['monto']
                            })
                    # Fallback a demo
                    return render(request, 'pago_oxxo.html', {
                        'orden': orden,
                        'referencia': '12345678901234',
                        'caducidad': '2024-12-31 23:59',
                        'monto': f'{total:.2f}'
                    })
                    
            except Exception as e:
                messages.error(request, f'Error al procesar la orden: {str(e)}')
                return redirect('carrito')
    
    else:
        initial_data = {'email': request.user.email} if request.user.is_authenticated else {}
        form = MetodoPagoForm(initial=initial_data)
    
    context = {
        'form': form,
        'subtotal': subtotal,
        'envio': envio,
        'total': total,
        'carrito': carrito_session
    }
    return render(request, 'seleccionar_pago.html', context)

@login_required
def pago_stripe(request):
    """Vista para procesar pago con Stripe"""
    return render(request, 'pago_stripe.html')

@login_required
def pago_oxxo(request):
    """Vista para procesar pago con OXXO"""
    return render(request, 'pago_oxxo.html')

@login_required
def recibo(request):
    """Vista para mostrar recibo"""
    return render(request, 'recibo.html')

@login_required
def pago_stripe_webhook(request):
    """Webhook para Stripe (para producción)"""
    try:
        import stripe
    except ImportError:
        return JsonResponse({'error': 'Stripe no instalado'}, status=400)
    
    if not hasattr(settings, 'STRIPE_WEBHOOK_SECRET'):
        return JsonResponse({'error': 'Webhook no configurado'}, status=400)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=400)
    
    # Manejar eventos
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        orden_id = payment_intent['metadata'].get('orden_id')
        
        if orden_id and MODELO_ORDEN_DISPONIBLE:
            try:
                orden = Orden.objects.get(id=orden_id)
                orden.estado = 'completado'
                orden.save()
            except Orden.DoesNotExist:
                pass
    
    return JsonResponse({'status': 'success'})

@login_required
def verificar_pago(request, orden_id):
    """Verifica el estado de un pago"""
    if not MODELO_ORDEN_DISPONIBLE:
        # Modo demostración
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
    
    # Modo real con base de datos
    try:
        orden = Orden.objects.get(id=orden_id, usuario=request.user)
    except Orden.DoesNotExist:
        messages.error(request, 'Orden no encontrada')
        return redirect('home')
    
    # Si es stripe, verificar estado
    if orden.metodo_pago == 'stripe' and orden.stripe_payment_intent_id:
        if PROCESADOR_PAGOS_DISPONIBLE:
            if ProcesadorPagos.verificar_pago_stripe(orden.stripe_payment_intent_id):
                orden.estado = 'completado'
                orden.save()
    
    # Generar recibo
    if PROCESADOR_PAGOS_DISPONIBLE:
        recibo = ProcesadorPagos.generar_recibo(orden)
    else:
        recibo = {
            'numero_orden': orden.id,
            'fecha': orden.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'cliente': orden.usuario.username,
            'email': orden.usuario.email,
            'total': f"${orden.total:.2f}",
            'metodo_pago': 'Tarjeta' if orden.metodo_pago == 'stripe' else 'OXXO',
            'estado': orden.estado.capitalize()
        }
    
    # Limpiar carrito después de pago exitoso
    if orden.estado == 'completado':
        if 'carrito' in request.session:
            del request.session['carrito']
            request.session.modified = True
    
    return render(request, 'recibo.html', {
        'orden': orden,
        'recibo': recibo
    })

@login_required
def historial_pedidos(request):
    """Muestra el historial de pedidos del usuario"""
    if not MODELO_ORDEN_DISPONIBLE:
        # Datos de demostración
        ordenes_demo = [
            type('obj', (), {
                'id': 1,
                'total': Decimal('150.00'),
                'metodo_pago': 'stripe',
                'estado': 'completado',
                'fecha_creacion': '2024-01-01 12:00:00',
                'get_metodo_pago_display': lambda: 'Tarjeta (Stripe)',
                'get_estado_display': lambda: 'Completado',
                'items': {
                    'all': lambda: [
                        type('obj', (), {
                            'nombre_producto': 'Galleta de Chocolate',
                            'cantidad': 3,
                            'precio': Decimal('18.00'),
                            'subtotal': lambda: Decimal('54.00')
                        })
                    ]
                }
            }),
            type('obj', (), {
                'id': 2,
                'total': Decimal('85.00'),
                'metodo_pago': 'oxxo',
                'estado': 'pendiente',
                'fecha_creacion': '2024-01-02 14:30:00',
                'get_metodo_pago_display': lambda: 'Efectivo (OXXO)',
                'get_estado_display': lambda: 'Pendiente',
                'items': {
                    'all': lambda: [
                        type('obj', (), {
                            'nombre_producto': 'Galleta de Vainilla',
                            'cantidad': 5,
                            'precio': Decimal('15.00'),
                            'subtotal': lambda: Decimal('75.00')
                        })
                    ]
                }
            })
        ]
        
        return render(request, 'historial_pedidos.html', {
            'ordenes': ordenes_demo,
            'total_orders': 2,
            'completed_orders': 1,
            'pending_orders': 1,
            'total_spent': Decimal('235.00')
        })
    
    # Modo real con base de datos
    ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    # Calcular estadísticas
    total_orders = ordenes.count()
    completed_orders = ordenes.filter(estado='completado').count()
    pending_orders = ordenes.filter(estado='pendiente').count()
    
    try:
        total_spent = sum([orden.total for orden in ordenes.filter(estado='completado')])
    except:
        total_spent = Decimal('0.00')
    
    context = {
        'ordenes': ordenes,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_spent': total_spent
    }
    
    return render(request, 'historial_pedidos.html', context)

# ============ ERROR HANDLING ============

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

def formulario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        asunto = request.POST.get('asunto', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        newsletter = request.POST.get('newsletter', False)
        
        # Validación básica
        errors = []
        if not nombre:
            errors.append('El nombre es obligatorio')
        if not email:
            errors.append('El email es obligatorio')
        if not asunto:
            errors.append('El asunto es obligatorio')
        if not mensaje:
            errors.append('El mensaje es obligatorio')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # 1. Enviar email al administrador
                email_admin = EmailMessage(
                    subject=f'Contacto Dalgona: {asunto}',
                    body=f'''
                    Nuevo mensaje de contacto:
                    
                    Nombre: {nombre}
                    Email: {email}
                    Asunto: {asunto}
                    Newsletter: {'Sí' if newsletter else 'No'}
                    
                    Mensaje:
                    {mensaje}
                    
                    ---
                    Enviado desde el formulario de contacto de Dalgona Cookies
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_EMAIL],
                    reply_to=[email]
                )
                email_admin.send()
                
                # 2. Enviar confirmación al usuario
                email_usuario = EmailMessage(
                    subject=f'Confirmación de contacto - Dalgona Cookies',
                    body=f'''
                    Hola {nombre},
                    
                    Hemos recibido tu mensaje correctamente. Nos pondremos en contacto contigo en las próximas 24 horas.
                    
                    Resumen de tu mensaje:
                    Asunto: {asunto}
                    
                    Te responderemos a: {email}
                    
                    Gracias por contactar con Dalgona Cookies.
                    
                    Atentamente,
                    El equipo de Dalgona Cookies
                    
                    ---
                    Calle Calzada Cetys #123, Tijuana, B.C.
                    Tel: +52 664 399 6945
                    Email: dalgona@gmail.com.mx
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                email_usuario.send()
                
                # 3. Guardar en base de datos si tienes modelo ContactMessage
                try:
                    from .models import ContactMessage
                    ContactMessage.objects.create(
                        nombre=nombre,
                        email=email,
                        asunto=asunto,
                        mensaje=mensaje,
                        newsletter=bool(newsletter)
                    )
                except:
                    pass  # Si no tienes el modelo, continúa
                
                messages.success(request, '¡Mensaje enviado correctamente! Te contactaremos pronto.')
                return redirect('formulario')
                
            except Exception as e:
                messages.error(request, f'Error al enviar el mensaje: {str(e)}')
    
    return render(request, 'formulario.html')

# Si quieres recibir notificaciones por webhook (opcional)
@csrf_exempt
def contacto_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Procesar datos del webhook
            nombre = data.get('nombre', '')
            email = data.get('email', '')
            mensaje = data.get('mensaje', '')
            
            # Aquí puedes integrar con CRM, Slack, etc.
            print(f"Webhook recibido de {nombre} ({email})")
            
            return JsonResponse({'status': 'success'}, status=200)
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'method not allowed'}, status=405)
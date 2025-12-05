import stripe
from django.conf import settings
from datetime import datetime, timedelta
import secrets
from .models import Orden

# Configura Stripe (agrega tu clave secreta en settings.py)
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeManager:
    @staticmethod
    def crear_pago_intent(orden):
        try:
            # Convertir a centavos para Stripe
            amount_cents = int(orden.total * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='mxn',
                payment_method_types=['card'],
                metadata={
                    'orden_id': orden.id,
                    'user_id': orden.usuario.id
                }
            )
            
            return {
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id
            }
        except Exception as e:
            print(f"Error Stripe: {e}")
            return None

class OXXOManager:
    @staticmethod
    def generar_referencia_oxxo(orden):
        # Generar referencia aleatoria de 14 dígitos
        referencia = ''.join(secrets.choice('0123456789') for _ in range(14))
        
        # Caducidad: 72 horas
        caducidad = datetime.now() + timedelta(hours=72)
        
        return {
            'referencia': referencia,
            'caducidad': caducidad.strftime('%Y-%m-%d %H:%M:%S'),
            'monto': f"{orden.total:.2f}"
        }

class ProcesadorPagos:
    @staticmethod
    def procesar_pago(orden, metodo_pago):
        if metodo_pago == 'stripe':
            return StripeManager.crear_pago_intent(orden)
        elif metodo_pago == 'oxxo':
            return OXXOManager.generar_referencia_oxxo(orden)
        return None
    
    @staticmethod
    def verificar_pago_stripe(payment_intent_id):
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent.status == 'succeeded'
        except:
            return False
    
    @staticmethod
    def generar_recibo(orden):
        # Aquí generas el recibo en PDF o HTML
        recibo_data = {
            'numero_orden': orden.id,
            'fecha': orden.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'cliente': orden.usuario.get_full_name() or orden.usuario.username,
            'email': orden.usuario.email,
            'total': f"${orden.total:.2f}",
            'metodo_pago': orden.get_metodo_pago_display(),
            'estado': orden.get_estado_display(),
        }
        
        if orden.metodo_pago == 'oxxo':
            recibo_data.update({
                'referencia_oxxo': orden.oxxo_referencia,
                'caducidad_oxxo': orden.oxxo_caducidad.strftime('%d/%m/%Y %H:%M') if orden.oxxo_caducidad else '',
                'instrucciones': 'Paga en cualquier tienda OXXO con la referencia proporcionada'
            })
        
        return recibo_data
    
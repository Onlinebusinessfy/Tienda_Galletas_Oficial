import os
import sys
import django
from django.core.mail import EmailMessage
from decouple import config

# 🔧 AGREGAR CONFIGURACIÓN DEL PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_main_TIENDA_GALLETAS.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    print("💡 Verifica que:")
    print("   1. La carpeta 'core_main_TIENDA_GALLETAS' exista")
    print("   2. El archivo 'settings.py' esté en esa carpeta")
    sys.exit(1)

def enviar_comprobante_pedido():
    """
    Envía un comprobante de pedido de galletas por correo electrónico
    con diseño HTML profesional para la tienda de galletas
    """
    # Datos del pedido 
    datos = {
        'pedido': 'PED-2024-001',
        'fecha': '2024-01-15',
        'hora': '14:30:00',
        'cliente': 'María González',
        'productos': [
            {'nombre': 'Galletas de Chocolate Premium', 'cantidad': 2, 'precio': 8.00},
            {'nombre': 'Galletas de Avena y Pasas', 'cantidad': 1, 'precio': 4.50},
            {'nombre': 'Mix Especial Dalgona', 'cantidad': 1, 'precio': 12.00},
        ],
        'total': 24.50,
        'estado': 'Confirmado',
        'tienda': 'Dalgona - Tienda de Galletas',
        'imagen_url': 'https://via.placeholder.com/150'
    }

    # Asunto del correo
    subject = f"🍪 Comprobante de Pedido: {datos['pedido']} - {datos['tienda']}"

    # Generar filas de productos para la tabla HTML
    filas_productos = ""
    for producto in datos['productos']:
        subtotal = producto['cantidad'] * producto['precio']
        filas_productos += f"""
        <tr>
            <td>{producto['nombre']}</td>
            <td style="text-align: center;">{producto['cantidad']}</td>
            <td style="text-align: right;">${producto['precio']:.2f}</td>
            <td style="text-align: right;">${subtotal:.2f}</td>
        </tr>
        """

    # Cuerpo HTML 
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Comprobante de Pedido - Tienda de Galletas</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #fff5f5;
                margin: 0;
                padding: 20px;
                color: #5a3921;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(90, 57, 33, 0.1);
            }}
            .header {{
                text-align: center;
                background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
                color: #5a3921;
                padding: 25px;
                border-radius: 15px 15px 0 0;
                margin: -30px -30px 25px -30px;
            }}
            .logo {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .tagline {{
                font-style: italic;
                font-size: 16px;
                opacity: 0.9;
            }}
            .status-confirmed {{
                background-color: #d4edda;
                color: #155724;
                padding: 12px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                margin: 20px 0;
                border-left: 4px solid #28a745;
            }}
            .details-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
                background: #fff9f9;
                border-radius: 10px;
                overflow: hidden;
            }}
            .details-table td {{
                padding: 14px;
                border-bottom: 1px solid #fad0c4;
            }}
            .details-table td:first-child {{
                font-weight: bold;
                width: 35%;
                color: #8b5a3c;
                background: #fef5f5;
            }}
            .products-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .products-table th {{
                background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
                color: #5a3921;
                padding: 15px;
                text-align: left;
                font-weight: bold;
            }}
            .products-table td {{
                padding: 12px;
                border-bottom: 1px solid #fad0c4;
            }}
            .products-table tr:hover {{
                background-color: #fff5f5;
            }}
            .total-section {{
                text-align: right;
                font-size: 20px;
                font-weight: bold;
                margin: 25px 0;
                padding: 15px;
                background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
                color: #5a3921;
                border-radius: 10px;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px dashed #fad0c4;
                text-align: center;
                color: #8b5a3c;
                font-size: 14px;
            }}
            .image-container {{
                text-align: center;
                margin: 20px 0;
            }}
            .image-container img {{
                border-radius: 15px;
                max-width: 150px;
                border: 3px solid #fad0c4;
            }}
            .cookie-emoji {{
                font-size: 24px;
                margin: 0 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">
                    <span class="cookie-emoji">🍪</span>
                    {datos['tienda']}
                    <span class="cookie-emoji">🍪</span>
                </div>
                <div class="tagline">Galletas que endulzan tu día</div>
            </div>

            <div class="status-confirmed">
                ✅ Pedido {datos['estado']} - ¡Estamos preparando tus galletas!
            </div>

            <table class="details-table">
                <tr>
                    <td>Número de Pedido:</td>
                    <td><strong>{datos['pedido']}</strong></td>
                </tr>
                <tr>
                    <td>Cliente:</td>
                    <td>{datos['cliente']}</td>
                </tr>
                <tr>
                    <td>Fecha del Pedido:</td>
                    <td>{datos['fecha']}</td>
                </tr>
                <tr>
                    <td>Hora:</td>
                    <td>{datos['hora']}</td>
                </tr>
                <tr>
                    <td>Tienda:</td>
                    <td>{datos['tienda']}</td>
                </tr>
            </table>

            <h3 style="color: #5a3921; margin-bottom: 15px;">📦 Productos del Pedido</h3>
            <table class="products-table">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th style="text-align: center;">Cantidad</th>
                        <th style="text-align: right;">Precio Unit.</th>
                        <th style="text-align: right;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_productos}
                </tbody>
            </table>

            <div class="total-section">
                Total del Pedido: <span style="font-size: 24px;">${datos['total']:.2f}</span>
            </div>

            <div class="image-container">
                <img src="{datos['imagen_url']}" alt="Galletas Deliciosas">
                <p style="margin-top: 10px; font-style: italic; color: #8b5a3c;">
                    ¡Tus galletas están siendo preparadas con mucho amor!
                </p>
            </div>

            <div class="footer">
                <p>📍 Av. Dulces 123, Ciudad Galleta</p>
                <p>📞 +1 234 567 890 • ✉️ hola@dalgona.com</p>
                <p style="margin-top: 15px; font-size: 12px; color: #a78b73;">
                    © 2024 {datos['tienda']}. Todos los derechos reservados.<br>
                    Este es un mensaje automático, por favor no responda a este correo.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    # Solicitar email del destinatario
    email_to = input("Ingrese el correo electrónico del destinatario: ")

    try:
        # Crear y enviar el correo
        email = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=config("EMAIL_HOST_USER"),
            to=[email_to],
        )
        
        # Especificar que es HTML
        email.content_subtype = "html"
        
        # Enviar correo
        email.send()
        
        print(f"✅ Comprobante de pedido enviado exitosamente a: {email_to}")
        print(f"📧 Asunto: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar el correo: {str(e)}")
        return False

# Ejecutar si se llama directamente
if __name__ == "__main__":
    print("🍪 SISTEMA DE ENVÍO DE COMPROBANTES - TIENDA DE GALLETAS")
    print("=" * 60)
    
    enviar_comprobante_pedido()
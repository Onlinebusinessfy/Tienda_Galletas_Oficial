# from django.db import models

# from .models import *

# class ModelXForm(models.ModelForm):
#     class Meta:
#         model = ModelX
#         fields = "__all__"
        
#         labels = {
#             'name':'Nombre',
#             'descripcion':'Descripción'
#         }

from django import forms
from .models import Orden
from .models import ContactMessage

class MetodoPagoForm(forms.Form):
    METODO_PAGO_CHOICES = [
        ('stripe', 'Tarjeta de crédito/débito'),
        ('oxxo', 'Pago en efectivo en OXXO'),
    ]
    
    metodo_pago = forms.ChoiceField(
        choices=METODO_PAGO_CHOICES,
        widget=forms.RadioSelect,
        label="Selecciona método de pago"
    )
    
    email = forms.EmailField(
        label="Email para envío de recibo",
        required=True
    )


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['nombre', 'email', 'asunto', 'mensaje', 'newsletter']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '¿En qué podemos ayudarte?'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu mensaje aquí...',
                'rows': 6
            }),
            'newsletter': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
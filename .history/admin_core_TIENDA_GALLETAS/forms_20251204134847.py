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
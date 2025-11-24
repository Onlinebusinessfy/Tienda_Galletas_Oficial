from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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

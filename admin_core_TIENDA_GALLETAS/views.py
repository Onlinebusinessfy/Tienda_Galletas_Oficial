from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'base.html')

def formulario(request):
    return render(request, 'formulario.html')

def about(request):
    return render(request, 'about.html')

def galleta(request):
    return render(request, 'galleta.html')

def orden(request):
    return render(request, 'orden.html')

def venta(request):
    return render(request, 'venta.html')

def detalle_venta(request):
    return render(request, 'detalle_venta.html')


from django.shortcuts import render
from apps.loginApp.models import User

def gotoProductos(request):
    user = User.objects.get(id = request.session['id'])
    context = {
        'tipo' : 'view', 
        'user' : user,
    }
    return render(request,'productos.html',context)

def editProductos(request):
    user = User.objects.get(id = request.session['id'])
    context = {
        'tipo' : 'edit', 
        'user' : user,
    }
    return render(request,'productos.html',context)

from django.http.response import JsonResponse
from apps.mantenedorApp.models import Area, TipoMov, Estado
from django.shortcuts import render, redirect
from apps.loginApp.models import User
from .models import MovItem, MovEstado, MovEncabezado, Stock
from django.contrib import messages

def gotoDashboard(request,id_user,tipo):
    context = {
        'id_user' : id_user,
        'tipo' : tipo,
        'user' : User.objects.get(id = request.session['id'])
    }
    return render(request,'dashboard.html',context)
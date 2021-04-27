
from django.http.response import JsonResponse
from apps.mantenedorApp.models import Area, TipoMov, Estado
from django.shortcuts import render, redirect
from apps.loginApp.models import User
from .models import MovItem, MovEstado, MovEncabezado, Stock
from django.contrib import messages

def gotoDashboard(request,id_user,tipo):
    if "id" in request.session:
        all_encabezados=MovEncabezado.objects.all()    
        all_areas=Area.objects.filter(is_active = True).order_by('pos')
        all_movimientos=TipoMov.objects.filter(is_active = True).order_by('pos')
        if len(User.objects.filter(id=id_user))>0:
            this_user= User.objects.get(id=id_user)
        else:
            this_user= User.objects.get(id=request.session["id"])
        mis_movimientos=[]
        for estado_mov in this_user.movs_asociados.all():
            mis_movimientos.append(estado_mov.mov_encabezado)
        print(mis_movimientos)
        context = {
            'id_user' : id_user,
            'tipo' : tipo,
            'user' : User.objects.get(id = request.session['id']),
            'all_encabezados':all_encabezados,
            'all_areas':all_areas,
            'all_movimientos':all_movimientos,
            'mis_movimientos':mis_movimientos
        }
        return render(request,'dashboard.html',context)
    return redirect("/")
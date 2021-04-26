
from django.http.response import JsonResponse
from apps.mantenedorApp.models import Area, TipoMov, Estado
from django.shortcuts import render, redirect
from apps.loginApp.models import User
from .models import MovEncabezado, MovItem, MovEstado, MovEncabezado, Stock
from .forms import NewMovEncabezadoForm, EditMovEncabezadoForm
from django.contrib import messages


def gotoDashboard(request,id_user,tipo):
    if "id" in request.session:
        all_encabezados=MovEncabezado.objects.all()    
        all_areas=Area.objects.all()
        all_movimientos=TipoMov.objects.all()
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


def requestNewMov(request):

    if request.method == "POST":
        if "id" in request.session:
            user = User.objects.filter(id=request.session["id"])
            if user:
                logged_user = user[0]
                area_id = request.POST["area"]
                tipo_mov_id = request.POST["tipo_mov"]
                return redirect("/movs/new?area=" + str(area_id) + "&"
                                + "tipo_mov=" + str(tipo_mov_id))
    return redirect("/")


def createNewMov(request):

    if not "id" in request.session:
        return redirect("/")
    user = User.objects.filter(id=request.session["id"])
    if not user:
        return redirect("/")
    logged_user = user[0]

    if request.method == "GET":
        initial_data = {}
        area_id = request.GET.get("area", 0)
        area = Area.objects.filter(id=area_id)
        if area:
            initial_data["area"] = area[0]
        tipo_mov_id = request.GET.get("tipo_mov", 0)
        tipo_mov = TipoMov.objects.filter(id=tipo_mov_id)
        if tipo_mov_id:
            initial_data["tipo_mov"] = tipo_mov[0]
        form = NewMovEncabezadoForm(initial=initial_data)
        
    if request.method == "POST":
        form = NewMovEncabezadoForm(request.POST)
        if form.is_valid():

            estado = Estado.objects.filter(name="CREADO")
            if not estado:
                return redirect("/")
            estado_creado = estado[0]

            new_mov_encabezado = MovEncabezado()
            new_mov_encabezado.descripcion = request.POST["descripcion"]
            # TODO: corregir, obviamente el folio no se obtiene así
            new_mov_encabezado.folio = 123456
            area = Area.objects.get(id=request.POST["area"])
            new_mov_encabezado.area = area
            tipo_mov = TipoMov.objects.get(id=request.POST["tipo_mov"])
            new_mov_encabezado.tipo_mov = tipo_mov
            new_mov_encabezado.save()

            new_mov_estado = MovEstado()
            new_mov_estado.mov_encabezado = new_mov_encabezado
            new_mov_estado.estado = estado_creado
            new_mov_estado.user = logged_user
            new_mov_estado.nota = ""
            new_mov_estado.save()

            return redirect("/movs/" + str(new_mov_encabezado.id))
    
    context = {
        "form": form,
        "button_txt": "Crear"
    }
    return render(request, "editMov.html", context)


def gotoMov(request, id_mov_encabezado):
    if "id" not in request.session:
        return redirect("/")
    user = User.objects.filter(id=request.session["id"])
    if not user:
        return redirect("/")
    logged_user = user[0]

    mov_encabezado = MovEncabezado.objects.filter(id=id_mov_encabezado)
    if not mov_encabezado:
        return redirect("/")
    mov_encabezado = mov_encabezado[0]

    if request.method == "POST":
        form = EditMovEncabezadoForm(request.POST)
        if form.is_valid():
            mov_encabezado.descripcion = request.POST["descripcion"]
            mov_encabezado.area = Area.objects.get(id=request.POST["area"])
            mov_encabezado.save()

    initial_data = {
        "descripcion": mov_encabezado.descripcion,
        "area": mov_encabezado.area
    }
    form = EditMovEncabezadoForm(initial=initial_data)
    context = {
        "form": form,
        "mov_encabezado": mov_encabezado,
        "button_txt": "Actualizar"
    }

    return render(request, "editMov.html", context)
  
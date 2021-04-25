
from django.http.response import JsonResponse
from apps.mantenedorApp.models import Area, TipoMov, Estado
from django.shortcuts import render, redirect
from apps.loginApp.models import User
from .models import MovEncabezado, MovItem, MovEstado, MovEncabezado, Stock
from .forms import NewMovForm
from django.contrib import messages


def gotoDashboard(request,id_user,tipo):
    context = {
        'id_user' : id_user,
        'tipo' : tipo,
        'user' : User.objects.get(id = request.session['id'])
    }
    return render(request,'dashboard.html',context)


def requestNewMov(request):

    if request.method == "POST":
        if "id" in request.session:
            user = User.objects.filter(id=request.session["id"])
            if user:
                logged_user = user[0]
                area_id = request.POST["area_id"]
                tipo_mov_id = request.POST["tipo_mov_id"]
                return redirect("/movs/new/?area=" + str(area_id) + "&"
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
        form = NewMovForm(initial=initial_data)
        
    if request.method == "POST":
        form = NewMovForm(request.POST)
        if form.is_valid():
            new_mov_encabezado = form.save(commit=False)
            # TODO: corregir, obviamente el folio no se obtiene así
            new_mov_encabezado.folio = 123456
            area = Area.objects.get(id=request.POST["area"])
            new_mov_encabezado.area = area
            tipo_mov = TipoMov.objects.get(id=request.POST["tipo_mov"])
            new_mov_encabezado.tipo_mov = tipo_mov
            new_mov_encabezado.save()
            return redirect("/movs/" + str(new_mov_encabezado.id) +"/edit")

    return render(request, "editMov.html", context={"form": form})

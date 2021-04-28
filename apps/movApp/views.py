
from django.http.response import JsonResponse
from apps.mantenedorApp.models import Area, TipoMov, Estado
from apps.productoApp.models import Producto
from django.shortcuts import render, redirect
from apps.loginApp.models import User
from .models import MovEncabezado, MovItem, MovEstado, MovEncabezado, Stock
from .forms import NewMovEncabezadoForm, EditMovEncabezadoForm, \
                   AddProductoToMovForm
from django.contrib import messages


def gotoDashboard(request,id_user,tipo):
    if "id" in request.session:
        all_encabezados=MovEncabezado.objects.all()    
        all_areas=Area.objects.filter(is_active = True).order_by('pos')
        all_movimientos=TipoMov.objects.filter(is_active = True).order_by('pos')
        print(id_user)

        if len(User.objects.filter(id=id_user))>0:
            this_user= User.objects.get(id=id_user)
        else:
            this_user= User.objects.get(id=request.session["id"])
        print(this_user)
        mis_encabezados=[]
        for estado_mov in this_user.movs_asociados.all():
            if estado_mov.mov_encabezado not in mis_encabezados:
                mis_encabezados.append(estado_mov.mov_encabezado)        
        context = {
            'id_user' : id_user,
            'tipo' : tipo,
            'user' : this_user,
            'all_encabezados':all_encabezados,
            'all_areas':all_areas,
            'all_movimientos':all_movimientos,
            'mis_encabezados':mis_encabezados,            
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
            area = Area.objects.get(id=request.POST["area"])
            new_mov_encabezado.area = area
            tipo_mov = TipoMov.objects.get(id=request.POST["tipo_mov"])
            new_mov_encabezado.tipo_mov = tipo_mov
            new_mov_encabezado.folio = tipo_mov.folio.num_folio
            new_mov_encabezado.save()

            folio = tipo_mov.folio
            folio.num_folio += 1
            folio.save()

            new_mov_estado = MovEstado()
            new_mov_estado.mov_encabezado = new_mov_encabezado
            new_mov_estado.estado = estado_creado
            new_mov_estado.user = logged_user
            new_mov_estado.nota = ""
            new_mov_estado.save()

            return redirect("/movs/view/" + str(new_mov_encabezado.id))
    
    context = {
        "encabezado_form": form,
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

    if mov_encabezado.estado == "CREADO":
        return redirect("/movs/solicitud/" + str(mov_encabezado.id))

    if mov_encabezado.estado == "SOLICITADO":
        # TODO: Esto debería redirigir a autorización
        return redirect("/")

    if mov_encabezado.estado == "AUTORIZADO":
        # TODO: Esto debería redirigir a ejecución
        return redirect("/")
    

def solicitud(request, id_mov_encabezado):
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

    if mov_encabezado.estado not in ["CREADO", "CANCELADO"]:
        return redirect("/")

    producto_form = AddProductoToMovForm()
    context = {}

    if request.method == "POST":

        if "descripcion" in request.POST:
            encabezado_form = EditMovEncabezadoForm(request.POST)
            if encabezado_form.is_valid():
                mov_encabezado.descripcion = request.POST["descripcion"]
                mov_encabezado.area = Area.objects.get(id=request.POST["area"])
                mov_encabezado.save()

        if "cant_solicitada" in request.POST:
            producto_form = AddProductoToMovForm(request.POST)
            if producto_form.is_valid():
                cod = request.POST["cod"]
                name = request.POST["name"]
                cant_solicitada = request.POST["cant_solicitada"]

                if len(cod) > 0:
                    producto = Producto.objects.filter(cod=cod)
                if len(name) > 0:
                    producto = Producto.objects.filter(name=name)

                if len(producto) == 0:
                    producto_form.add_error("cod", "Producto no encontrado")
                if len(producto) > 1:
                    context["posibles_productos"] = producto
                if len(producto) == 1:
                    MovItem.objects.create(
                        mov_encabezado=mov_encabezado,
                        producto=producto[0],
                        cant_solicitada=request.POST["cant_solicitada"]
                    )

    initial_data = {
        "descripcion": mov_encabezado.descripcion,
        "area": mov_encabezado.area
    }
    encabezado_form = EditMovEncabezadoForm(initial=initial_data)

    context["encabezado_form"] = encabezado_form
    context["producto_form"] = producto_form
    context["mov_encabezado"] = mov_encabezado
    context["button_txt"] = "Actualizar"

    context["user_solicitando"] = False
    if mov_encabezado.estado == "CREADO":
        mov_estado_creado = mov_encabezado.mov_estados \
                            .get(estado__name="CREADO")
        if mov_estado_creado.user == logged_user:
            context["user_solicitando"] = True

    return render(request, "editMov.html", context)
  

def solicitar_cancelar(request, id_mov_encabezado):

    # NOTE: se requiere dos formularios con campo oculto
    # cuyos valores son CANCELAR y SOLICITAR, en variable `action`
    if request.method == "POST":
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
    
        if mov_encabezado.estado != "CREADO":
            return redirect("/")
        mov_estado_creado = mov_encabezado.mov_estados.get(estado__name="CREADO")
    
        action = request.POST["action"]
        if action not in ["SOLICITAR", "CANCELAR"]:
            return redirect("/")
        
        if action == "SOLICITAR":
            estado = Estado.objects.filter(name="SOLICITADO")
        if action == "CANCELAR":
            estado = Estado.objects.filter(name="CANCELADO")
        if not estado:
            return redirect("/")
        estado = estado[0]
        
        new_mov_estado = MovEstado()
        new_mov_estado.mov_encabezado = mov_encabezado
        new_mov_estado.estado = estado
        new_mov_estado.user = logged_user
        new_mov_estado.nota = mov_estado_creado.nota
        new_mov_estado.save()

        if action == "SOLICITAR":
            for mov_item in mov_encabezado.mov_items.all():
                mov_item.cantidad_autorizada = mov_item.cantidad_solicitada
                mov_item.save()

    return redirect("/movs/" + str(logged_user.id) + "/activemov")
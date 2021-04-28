
from django.http.response import JsonResponse, HttpResponse
from apps.mantenedorApp.models import Area, TipoMov, Estado
from apps.productoApp.models import Producto
from django.shortcuts import render, redirect
from apps.loginApp.models import User
from .models import MovEncabezado, MovItem, MovEstado, MovEncabezado, Stock
from .forms import NewMovEncabezadoForm, EditMovEncabezadoForm, \
                   AddProductoToMovForm
from django.contrib import messages
from .utils import render_to_pdf


def gotoDashboard(request, id_user, tipo):
    if "id" in request.session:
        
        all_encabezados = MovEncabezado.objects.all()
        all_areas = Area.objects.filter(is_active=True).order_by('pos')
        all_movimientos = TipoMov.objects.filter(
            is_active=True).order_by('pos')
        print(id_user)

        user = User.objects.get(id=request.session["id"])

        if len(User.objects.filter(id=id_user)) > 0:
            user_dash = User.objects.get(id=id_user)
        else:
            user_dash = user
        
        mis_encabezados = []
        for estado_mov in user_dash.movs_asociados.all():
            if estado_mov.mov_encabezado not in mis_encabezados:
                mis_encabezados.append(estado_mov.mov_encabezado)
        context = {
            'user_dash': user_dash,
            'tipo': tipo,
            'user': user,
            'all_encabezados': all_encabezados,
            'all_areas': all_areas,
            'all_movimientos': all_movimientos,
            'mis_encabezados': mis_encabezados,
        }
        return render(request, 'dashboard.html', context)
    return redirect("/")


def requestNewMov(request):

    if request.method == "POST":
        if "id" in request.session:
            user = User.objects.filter(id=request.session["id"])
            if user:
                logged_user = user[0]
                if ("area" not in request.POST
                    or "tipo_mov" not in request.POST):
                    return redirect("/movs/0/activemov")
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
        "user_creando": True
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
        areas_para_autorizar = logged_user.areas_para_autorizar.all()
        tipos_para_autorizar = logged_user.tipos_para_autorizar.all()
        if (mov_encabezado.area in areas_para_autorizar
                and mov_encabezado.tipo_mov in tipos_para_autorizar) or (logged_user.isAdmin):
            return redirect("/movs/autorizacion/" + str(mov_encabezado.id))
        areas_para_ver = logged_user.areas_para_solicitar.all() \
                  .union(logged_user.areas_para_ejecutar.all())
        tipos_para_ver = logged_user.tipos_para_solicitar.all() \
                  .union(logged_user.tipos_para_ejecutar.all())
        if (mov_encabezado.area in areas_para_ver
                and mov_encabezado.tipo_mov in tipos_para_ver) or (logged_user.isAdmin):
            return redirect("/movs/solicitud/" + str(mov_encabezado.id))
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

    if mov_encabezado.estado not in ["CREADO", "CANCELADO", "SOLICITADO"]:
        return redirect("/")

    producto_form = AddProductoToMovForm()
    context = {} 
    print("////////////////////////////////")

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

    context["user_solicitando"] = False
    if mov_encabezado.estado == "CREADO":
        mov_estado_creado = mov_encabezado.mov_estados \
                            .get(estado__name="CREADO")
        if mov_estado_creado.user == logged_user:
            context["user_solicitando"] = True

    return render(request, "editMov.html", context)
  

def autorizacion(request, id_mov_encabezado):
    return HttpResponse("acá va la autorización")


def eliminarItem(request, id_mov_encabezado):
    # NOTE: Falta no permitir que otro usuario modifique el formulario
    # y elimine un item de otro movimiento, o al menos de un movimiento
    # que no le corresponde
    if "id" not in request.session:
        return redirect("/")
    user = User.objects.filter(id=request.session["id"])
    if not user:
        return redirect("/")

    try:
        item = MovItem.objects.get(id=request.POST["id_item"])
        item.delete()
        return redirect(f"/movs/view/{id_mov_encabezado}")
    except:
        pass


def editarItem(request, id_mov_encabezado):
    # NOTE: Falta no permitir que otro usuario modifique el formulario
    # y edite un item de otro movimiento, o al menos de un movimiento
    # que no le corresponde
    if "id" not in request.session:
        return redirect("/")
    user = User.objects.filter(id=request.session["id"])
    if not user:
        return redirect("/")

    try:
        item = MovItem.objects.get(id=request.POST["id_item"])
        print(item.producto.name)
        item.cant_solicitada = request.POST["quantity"]
        print(item.cant_solicitada)
        item.save()
        return redirect(f"/movs/view/{id_mov_encabezado}")
    except:
        return redirect(f"/movs/view/{id_mov_encabezado}")


def cambiarEstado(request, id_mov_encabezado):
    # NOTE: falta tener mucho cuidado con los permisos para que
    # no sea posible pasarlos por alto si se modifican los
    # formularios en el html
    if "id" not in request.session:
        return redirect("/")
    user = User.objects.filter(id=request.session["id"])
    if not user:
        return redirect("/")
    logged_user = user[0]
    try:
        new_estado = Estado.objects.get(name=request.POST['new_status'])
        mov = MovEncabezado.objects.get(id=id_mov_encabezado)
        new_mov_estado = MovEstado()
        new_mov_estado.mov_encabezado = mov
        new_mov_estado.estado = new_estado
        new_mov_estado.user = logged_user
        new_mov_estado.nota = ""
        new_mov_estado.save()

        if new_estado.name == "SOLICITADO":
            for mov_item in mov.mov_items.all():
                mov_item.cantidad_autorizada = mov_item.cantidad_solicitada
                mov_item.save()

        return redirect('/movs/0/activemov')
    except:
        return redirect("/")


def sacarPDF(request, id_mov_encabezado):
    mov = MovEncabezado.objects.get(id=id_mov_encabezado)
    mov_solicitado = MovEstado.objects.filter(mov_encabezado=mov)
    print(mov_solicitado)
    data = {
        'mov_encabezado': mov,
        'movimientos': mov_solicitado
    }
    pdf = render_to_pdf('pdf.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

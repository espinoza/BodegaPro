
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
from datetime import datetime
from BodegaPro.settings import MEDIA_URL

# MISC


def getUserCreandoAreasPermitidas(user: User):

    pass

    # if user.isAdmin:
    #    return Area.objects.filter(is_active=True).order_by('pos')
    # elif user.puedeSolicitar:
    #    return user.areas_para_solicitar.filter(is_active=True).distinct('pos').order_by('pos')

    tipos_mov = TipoMov.objects.filter(is_active=True).order_by('pos')

    # Dict de dicts con clave tipoMov.id
    tablaAreasXTipoMov = {}
    for tipo_mov in tipos_mov:
        print(tipo_mov)
        tablaAreasXTipoMov[tipo_mov.id] = User.objects.areasQue(
            'solicita', tipo_mov, user)

    print(tablaAreasXTipoMov)

    return tablaAreasXTipoMov


# ROUTES
def gotoDashboard(request, id_user, tipo):

    if "id" in request.session:

        if tipo != "activemov" and tipo != 'allmov':
            return redirect("/")

        user = User.objects.get(id=request.session["id"])

        #all_areas = getUserCreandoAreasPermitidas(user)

        if user.isAdmin:
            all_areas = Area.objects.filter(is_active=True).order_by('pos')
            all_movimientos = TipoMov.objects.filter(is_active=True).order_by('pos')
        elif user.puedeSolicitar:
            all_areas = user.areas_para_solicitar.filter(is_active=True).distinct('pos').order_by('pos')
            all_movimientos = user.tipos_para_solicitar.filter(is_active=True).distinct('pos').order_by('pos')

        context = {}

        if len(User.objects.filter(id=id_user)) > 0:
            user_dash = User.objects.get(id=id_user)
        else:
            user_dash = user

        if id_user == 0:
            mis_o_todos = 'todos'
            encabezados = MovEncabezado.objects.all()
        else:
            mis_o_todos = 'mis'
            encabezados = []
            for estado_mov in user_dash.movs_asociados.all():
                if (estado_mov.user.id == user_dash.id and estado_mov.estado.name == 'CREADO' ) and \
                     (estado_mov.mov_encabezado not in encabezados):
                    encabezados.append(estado_mov.mov_encabezado)

        context = {
            'tipo': tipo,
            'user': user,
            'user_dash' : user_dash,
            'encabezados': encabezados,
            'all_areas': all_areas,
            'all_movimientos': all_movimientos,
            'mis_o_todos':mis_o_todos,
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
        "user_creando": True,
        "user": logged_user,
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

    areas_para_ver = logged_user.areas_para_solicitar.all() \
        .union(logged_user.areas_para_autorizar.all()) \
        .union(logged_user.areas_para_ejecutar.all())
    tipos_para_ver = logged_user.tipos_para_solicitar.all() \
        .union(logged_user.tipos_para_autorizar.all()) \
        .union(logged_user.tipos_para_ejecutar.all())
    if not ( (mov_encabezado.area in areas_para_ver
              and mov_encabezado.tipo_mov in tipos_para_ver)
             or (logged_user.isAdmin) ):
        return redirect("/")

    context = {}
    if mov_encabezado.estado == "CREADO":

        producto_form = AddProductoToMovForm()

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
                        producto_form.add_error(
                            "cod", "Producto no encontrado"
                        )
                    if len(producto) > 1:
                        context["posibles_productos"] = producto

                    if len(mov_encabezado.mov_items
                            .filter(producto=producto[0].id))>0:
                        producto_form.add_error(
                            "cod", "Producto ya ingresado. Edite la cantidad."
                        )
                    elif len(producto) == 1:
                        MovItem.objects.create(
                            mov_encabezado=mov_encabezado,
                            producto=producto[0],
                            cant_solicitada=request.POST["cant_solicitada"]
                        )

        initial_data = {
            "descripcion": mov_encabezado.descripcion,
            "area": mov_encabezado.area,
        }
        encabezado_form = EditMovEncabezadoForm(initial=initial_data)

        context["encabezado_form"] = encabezado_form
        context["producto_form"] = producto_form

    context["mov_encabezado"] = mov_encabezado
    context["user_solicitando"] = False
    context["user_autorizando"] = False
    context["user_ejecutando"] = False

    if mov_encabezado.estado == "CREADO":
        mov_estado_creado = mov_encabezado.mov_estados \
            .get(estado__name="CREADO")
        if mov_estado_creado.user == logged_user:
            context["user_solicitando"] = True
            context['media_url'] = MEDIA_URL

    if mov_encabezado.estado == "SOLICITADO":
        areas_para_autorizar = logged_user.areas_para_autorizar.all()
        tipos_para_autorizar = logged_user.tipos_para_autorizar.all()
        if ( (mov_encabezado.area in areas_para_autorizar
              and mov_encabezado.tipo_mov in tipos_para_autorizar)
                or (logged_user.isAdmin) ):
            context["user_autorizando"] = True

    if mov_encabezado.estado == "AUTORIZADO":
        areas_para_ejecutar = logged_user.areas_para_ejecutar.all()
        tipos_para_ejecutar = logged_user.tipos_para_ejecutar.all()
        if ( (mov_encabezado.area in areas_para_ejecutar
              and mov_encabezado.tipo_mov in tipos_para_ejecutar)
                or (logged_user.isAdmin) ):
            context["user_ejecutando"] = True

    context["user"] = logged_user

    return render(request, "editMov.html", context)


def eliminarItem(request, id_mov_encabezado):
    # NOTE: Falta no permitir que otro usuario modifique el formulario
    # y elimine un item de otro movimiento, o al menos de un movimiento
    # que no le corresponde
    if "id" not in request.session:
        return redirect("/")
    user = User.objects.filter(id=request.session["id"])
    if not user:
        return redirect("/")

    item = MovItem.objects.filter(id=request.POST["id_item"])
    if not item:
        return redirect("/")
    item = item[0]
    item.delete()
    return redirect(f"/movs/view/{id_mov_encabezado}")


def editarItem(request, id_mov_encabezado):
    # NOTE: Falta no permitir que otro usuario modifique el formulario
    # y edite un item de otro movimiento, o al menos de un movimiento
    # que no le corresponde
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

    item = MovItem.objects.filter(id=request.POST["id_item"])
    if not item:
        return redirect("/")
    item = item[0]

    print(item.producto.name)
    if mov_encabezado.estado == "CREADO":
        item.cant_solicitada = request.POST["quantity"]
        print(item.cant_solicitada)
    elif mov_encabezado.estado == "SOLICITADO":
        item.cant_autorizada = request.POST["quantity"]
        print(item.cant_autorizada)
    elif mov_encabezado.estado == "AUTORIZADO":
        item.cant_ejecutada = request.POST["quantity"]
        print(item.cant_ejecutada)
    item.save()

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
    mov_encabezado = MovEncabezado.objects.filter(id=id_mov_encabezado)
    if not mov_encabezado:
        return redirect("/")
    mov_encabezado = mov_encabezado[0]

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
                mov_item.cant_autorizada = mov_item.cant_solicitada
                mov_item.save()

        if new_estado.name == "AUTORIZADO":
            for mov_item in mov.mov_items.all():
                mov_item.cant_ejecutada = mov_item.cant_autorizada
                mov_item.save()

        if new_estado.name == "EJECUTADO":
            modificarStock(mov)
            return redirect("/productos/view")

        if new_estado.name in ["CANCELADO", "NO AUTORIZADO", "EJECUTADO"]:
            for mov_item in mov.mov_items.all():
                mov_item.stock_antes_de_cerrar = \
                    mov_item.producto.stock_data.cantidad
                mov_item.precio_unit = mov_item.producto.precio_unit
                mov_item.save()
            return redirect(f"/movs/view/{id_mov_encabezado}")

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


def sacarPDFstock(request):
    stocks = Stock.objects.filter(cantidad__gt=0)
    cantidad_productos = stocks.count()
    total_productos = sum([item.cantidad for item in stocks])
    total_plata = sum([item.monto_total for item in stocks])
    data = {
        'stocks': stocks,
        'hora': datetime.now,
        'cant_prod': cantidad_productos,
        'tot_prod': total_productos,
        'tot_plata': total_plata
    }
    pdf = render_to_pdf('pdfStock.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


def sacarPDFSinstock(request):
    stocks = Stock.objects.filter(cantidad=0)
    cantidad_productos = stocks.count()

    data = {
        'stocks': stocks,
        'hora': datetime.now,
        'cant_prod': cantidad_productos,

    }
    pdf = render_to_pdf('pdfSinStock.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


def modificarStock(mov):
    ponderador = mov.tipo_mov.folio.signo_stock
    print(ponderador)
    items = mov.mov_items.all()
    for item in items:
        producto_a_modificar = Producto.objects.get(id=item.producto.id)
        stock_a_modificar = Stock.objects.get(id=producto_a_modificar.id)
        # Sacamos precio
        if stock_a_modificar.cantidad != 0:
            precio_actual = stock_a_modificar.monto_total/stock_a_modificar.cantidad

        else:

            precio_actual = 0
        # Modificamos cantidad. Si es entrada, el ponderador será +1. Si es salida restar+a

        stock_a_modificar.cantidad += item.cant_ejecutada*ponderador
        stock_a_modificar.save()

        # Modificamos monto total
        if ponderador == 1:
            stock_a_modificar.monto_total += item.precio_unit*item.cant_ejecutada
        else:
            stock_a_modificar.monto_total -= precio_actual*item.cant_ejecutada
        stock_a_modificar.save()

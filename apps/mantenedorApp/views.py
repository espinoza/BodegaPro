from django.http import JsonResponse
from django.shortcuts import render, redirect
from apps.loginApp.models import User
from .models import Area, Estado, Familia, TipoMov, UnidadMedida
from django.contrib import messages

# Create your views here.

TABLAS = {
    'area' : 'AREA',
    'tipo_mov' : 'TIPO MOVIMIENTO',
    'estado_mov' : 'ESTADO MOV',
    'familia' : 'FAMILIA',
    'unidad_medida' : 'UNIDAD MEDIDA',
    #'folio' : 'FOLIO',
    #'tipo_medida' : 'TIPO MEDIDA
}

#CRUD
    
def addFilaToDB(post_data):
    #tabla_name, pos, name
    tabla = getTabla(post_data['tabla_name'])
    fila = tabla.create(
        pos = int(post_data['pos']),
        name = post_data['name'],
    )
    return fila

def updateFilaOnDB(post_data):
    tabla = getTabla(post_data['tabla_name'])

    fila = tabla.get(id = int(post_data['id']))

    if 'pos' in post_data:
        fila.pos = int(post_data['pos'])
    
    if 'name' in post_data:
        fila.name = post_data['name']
    
    fila.save()

    return fila

#MISC

def getTabla(tabla_name):
    if tabla_name == 'area':
        tabla = Area.objects
    elif tabla_name == 'tipo_mov':
        tabla= TipoMov.objects
    elif tabla_name == 'estado_mov':
        tabla = Estado.objects
    elif tabla_name == 'familia':
        tabla = Familia.objects
    elif tabla_name == 'unidad_medida':
        tabla = UnidadMedida.objects
    else:
        return False
    return tabla

#ROUTES
def gotoMantenedor(request,tabla_name):

    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    user = User.objects.get(id = request.session['id'])

    context = {
        'user' : user,
        'tablas' : TABLAS,
        'tabla_name' : tabla_name,
        'tabla_data' : Area.objects.all(), #por elegir una tabla por defecto
    }

    return render(request, "mantenedor.html", context)

def loadTabla(request): #AJAX

    if User.objects.get(id = request.session['id']).isAdmin and request.method == "POST":

        tabla = getTabla(request.POST["tabla_name"])
        tabla_data = tabla.all().order_by('pos')

        return JsonResponse(
                list(tabla_data.values('id','name','pos','is_active')),
                safe=False
            )

    else:

        return redirect('signin')


def toggleItemTabla(request): #AJAX

    if User.objects.get(id = request.session['id']).isAdmin and request.method == "POST":

        response = {}

        try:
            tabla = getTabla(request.POST["tabla_name"])
            filas = tabla.filter(id = int(request.POST['id']))
        except:
            response['status'] = f"Tabla '{request.POST['tabla_name']}' no encontrada!"
            return JsonResponse(response)

        if len(filas) > 0:
            fila = filas[0]
            if request.POST['is_active'] == 'false':
                is_active = False
            else:
                is_active = True

            #update is_active
            fila.is_active = is_active
            fila.save()
            
            response = {
                'status' : 'OK',
                'name' : fila.name,
                'pos' : fila.pos,
            }
        else:
            response['status'] = f"ID de la fila no encontrado en '{request.POST['tabla_name']}'!"
            
        return JsonResponse(response)

    else:

        return redirect('signin')


def newItemTabla(request):

    return (addOrUpdateItemTabla(request,'add'))

def updateItemTabla(request):

    return (addOrUpdateItemTabla(request,'update'))


def addOrUpdateItemTabla(request,tipo):

    if User.objects.get(id = request.session['id']).isAdmin and request.method == "POST":

        response = {} 

        if (tipo == 'add'):
            exclude_id = 0
        else:
            exclude_id = request.POST['id']

        #try:
        print(request.POST["tabla_name"])
        tabla = getTabla(request.POST["tabla_name"])
        errors = tabla.mantenedor_validator(request.POST,exclude_id)
        #except:
        #    response['status'] = f"Tabla '{request.POST['tabla_name']}' no encontrada!"
        #    return JsonResponse(response)


        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value) 

            return JsonResponse(errors)

        else:

            #Crear fila
            if tipo == 'add':
                fila = addFilaToDB(request.POST) #va con tabla_name!
            else: #'update'
                fila = updateFilaOnDB(request.POST) #tabla_name, id, pos, name
            
            response["status"] = "OK"

            return JsonResponse(response)

    else:

        return redirect('signin')


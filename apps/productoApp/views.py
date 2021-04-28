from apps.movApp.models import Stock
from apps.productoApp.models import Producto
from apps.mantenedorApp.models import Familia, UnidadMedida
from django.http import JsonResponse
from django.shortcuts import render, redirect
from apps.loginApp.models import User
from django.contrib import messages
from BodegaPro.settings import MEDIA_URL, MEDIA_ROOT
from datetime import datetime
import os

from django.core.files.storage import FileSystemStorage

#CRUD

def getUnidadesDB():
    return UnidadMedida.objects.filter(is_active = True)

def getFamiliasDB():
    return Familia.objects.filter(is_active = True )


def updateProductoDB(post_data,file_data):

    id_prod = int(post_data['id'])
    try:
        producto = Producto.objects.get(id = id_prod)
    except:
        return False
    
    if "cod" in post_data:
        producto.cod = post_data['cod']

    if "name" in post_data:
        producto.name = post_data['name'].upper()

    if "unidad_medida" in post_data:
        producto.unidad_medida = \
            UnidadMedida.objects.get(id = int(post_data['unidad_medida']))

    if "familia" in post_data:
        producto.familia= \
            Familia.objects.get(id = int(post_data['familia']))

    if len(file_data) > 0:
        addImageToProd(producto,file_data,'update')

    producto.save()

    return producto


def addProductoToDB(post_data,file_data):

    unidad_medida = UnidadMedida.objects.get(id = int(post_data['unidad_medida']))
    familia = Familia.objects.get(id = int(post_data['familia']))

    producto = Producto.objects.create(
        cod = int(post_data['cod']),
        name = post_data['name'].upper(),
        unidad_medida = unidad_medida,
        familia = familia,
        #img_url = fileName,
    )

    addImageToProd(producto,file_data)
    producto.save()

    #Crear Stock
    Stock.objects.create(
        producto = producto,
    )

    return producto



#MISC

def addImageToProd(producto: Producto,file_data,tipo='new'):

    #Manejo del Archivo
    #1. borrar archivos preexistentes
    folderName = "media/" + str(producto.id)
    folderPath = os.path.join(folderName)
    if os.path.exists(folderPath):
        with os.scandir(folderName) as files:
            for f in files:
                try:
                    os.remove(f)
                    print(f"file {f} removed!")
                except:
                    pass
    
    if len(file_data) > 0:
        sistemaArchivos = FileSystemStorage('media/' + str(producto.id)) 
        archivoCargado = file_data['img_url']
        extension = archivoCargado.name.lower().split('.')[-1]
        prefix = str(datetime.now()).replace(' ','H').replace('-','R').replace(':','D').replace('.','P')
        fileName = f"{prefix}__{producto.cod}.{extension}"
        miArchivo = sistemaArchivos.save(fileName,archivoCargado)
        producto.img_url = f"{producto.id}/{fileName}"
    elif tipo == 'new':
        fileName = '00000000.png'
        producto.img_url = fileName

#    try:
#        os.remove(os.path.join(MEDIA_ROOT, fileName))
#    except:
#        print('se sale del try del os.remove')
#        pass


def getProductoJson(producto):
    return {
        'id'            : producto.id,
        'img_url'       : f"{MEDIA_URL}{producto.img_url}",
        'cod'           : producto.cod,
        'name'          : producto.name,
        'cantidad'      : producto.cantidad,
        'unidad_medida' : producto.unidad_medida.name,
        'familia'       : producto.familia.name, 
        'precio_unit'   : producto.precio_unit,
        'is_active'     : producto.is_active,
    }

def productsToJson(filteredProducts):
    prodsJson = {}
    for p in filteredProducts:
        prodsJson[str(p.id)] = getProductoJson(p)
    return prodsJson


def prodFilter(isactive=1,familia=0,wordSet={}):

    if isactive == 1:
        q1 = Producto.objects.filter(is_active = True).order_by('name')
    elif isactive == -1:
        q1 = Producto.objects.filter(is_active = False).order_by('name')
    else:
        q1 = Producto.objects.all().order_by('name')

    try:
        familia_id = int(familia)
    except:
        familia_id = familia

    if familia_id > 0:
        q1 = q1.filter(familia__id=familia_id)

    for word in wordSet:
        q1 = q1.filter(name__icontains=word)

    return q1


#ROUTES
def gotoProductos(request):
    user = User.objects.get(id = request.session['id'])
    context = {
        'tipo' : 'view', 
        'user' : user,
        #'productos' : Producto.objects.filter(is_active = True),
        'familias' : getFamiliasDB(),
        'media_url' : MEDIA_URL,
    }
    return render(request,'productos.html',context)


def editProductos(request):

    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    user = User.objects.get(id = request.session['id'])
    if not user.isAdmin:
        return redirect('viewpproductos')

    context = {
        'tipo' : 'edit',
        'user' : user,
        'unidades' : getUnidadesDB(),
        'familias' : getFamiliasDB(),
        #'productos' : Producto.objects.all(),
        'media_url' : MEDIA_URL,
    }
    return render(request,'productos.html',context)


def updateProduct(request):

    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    user = User.objects.get(id = request.session['id'])
    if not user.isAdmin:
        return redirect('dashboard')

    if request.method == "POST":

        response = {}

        errors = Producto.objects.producto_validator(request.POST)

        if len(request.FILES) > 0 and not Producto.objects.is_valid_file_extension(request.FILES):
                errors['img_url'] = "Formato de archivo inválido (de ser .jpg, .png, .jpeg, .gif)"

        if len(errors) > 0:
            
            response['errores'] = errors
            response['status'] = 'error'

            return JsonResponse(response)

        else:

            producto = updateProductoDB(request.POST,request.FILES)

            response = {
                'status'        : 'OK',
                'product'       : getProductoJson(producto),
            }

            return JsonResponse(response)

    else:

        return redirect('viewproductos') 

def newProduct(request):

    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    user = User.objects.get(id = request.session['id'])
    if not user.isAdmin:
        return redirect('dashboard')

    if request.method == "POST":

        errors = Producto.objects.producto_validator(request.POST)

        if len(request.FILES) > 0 and not Producto.objects.is_valid_file_extension(request.FILES):
                errors['img_url'] = "Formato de archivo inválido (de ser .jpg, .png, .jpeg, .gif)"

        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value) 

            producto = Producto(
                cod=request.POST['cod'],
                name=request.POST['name'],
            )

            if 'unidad_medida' in request.POST:
                producto.unidad_medida = UnidadMedida.objects.get(id = int(request.POST['unidad_medida']))

            if 'familia' in request.POST:
                producto.familia = Familia.objects.get(id = int(request.POST['familia']))

            context = {
                'tipo' : 'edit',
                'user' : user,
                'new_product' : producto,
                'unidades' : getUnidadesDB(),
                'familias' : getFamiliasDB(),
                'productos' : Producto.objects.all(),
                'media_url' : MEDIA_URL,
            }

            return render(request,'productos.html',context)

        
        else:

            producto = addProductoToDB(request.POST,request.FILES)

            messages.success(request, f"Producto {producto.cod} {producto.name} creado!")
            
            return redirect('editproductos')

    else:

        return redirect('viewproductos')



def toggleItemProducto(request): #AJAX

    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    if User.objects.get(id = request.session['id']).isAdmin and request.method == "POST":

        response = {}

        productos = Producto.objects.filter(id = int(request.POST['id']))

        if len(productos) > 0:
            producto: Producto = productos[0]
            if request.POST['is_active'] == 'false':
                is_active = False
            else:
                is_active = True

            #update is_active
            producto.is_active = is_active
            producto.save()

            response = {
                'status'        : 'OK',
                'product'       : getProductoJson(producto),
            }

        else:
            response['status'] = "Id del producto no encontrado!"
            
        print(request.META.get('HTTP_X_FORWARDED_FOR'))
        print(request.META.get("REMOTE_ADDR"))
        

        return JsonResponse(response)

    else:

        return redirect('viewproductos')


def getFilteredProducts(request):

    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    response = {}

    if request.method == "POST":
        
        print(request.POST)

        if "isactive" in request.POST:
            isactive = int(request.POST["isactive"])
        else:
            isactive = 1

        if "contains" in request.POST:
            contiene_list = request.POST['contains'].split(' ')
            contiene = set(contiene_list)
        else:
            contiene = {}

        if "familias" in request.POST:
            familias = request.POST['familias']
        else:
            familias = 0

        print(isactive)
        print(contiene)
        print(familias)

        filteredProducts = prodFilter(isactive,familias,contiene)
        jsonProducts = productsToJson(filteredProducts)

        response['status'] = "OK"
        response['productos'] = jsonProducts

    else:

        response["status"] = "error: ruta inhabilitada"
    
    return JsonResponse(response)

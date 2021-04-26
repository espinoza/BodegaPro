
from apps.movApp.models import Stock
from apps.productoApp.models import Producto
from apps.mantenedorApp.models import Familia, UnidadMedida
from django.shortcuts import render, redirect
from apps.loginApp.models import User
from django.contrib import messages

from django.core.files.storage import FileSystemStorage

#CRUD

def getUnidadesDB():
    return UnidadMedida.objects.filter(is_active = True)

def getFamiliasDB():
    return Familia.objects.filter(is_active = True )

def addProductoToDB(post_data,file_data):

    unidad_medida = UnidadMedida.objects.get(id = int(post_data['unidad_medida']))
    familia = Familia.objects.get(id = int(post_data['familia']))

    #Manejo del Archivo
    if len(file_data) > 0:
        archivoCargado = file_data['img_url']
        extension = archivoCargado.name.lower().split('.')[-1]
        sistemaArchivos = FileSystemStorage('media/') 
        fileName = f"{post_data['cod']}.{extension}"
        miArchivo = sistemaArchivos.save(fileName,archivoCargado)
    else:
        fileName = '00000000.png'

    producto = Producto.objects.create(
        cod = int(post_data['cod']),
        name = post_data['name'].upper(),
        unidad_medida = unidad_medida,
        familia = familia,
        img_url = fileName,
    )

    #Crear Stock
    Stock.objects.create(
        producto = producto,
    )

    return producto



#ROUTES
def gotoProductos(request):
    user = User.objects.get(id = request.session['id'])
    context = {
        'tipo' : 'view', 
        'user' : user,
        'productos' : Producto.objects.filter(is_active = True),
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
        'productos' : Producto.objects.all(),
    }
    return render(request,'productos.html',context)


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
            }

            return render(request,'productos.html',context)

        
        else:

            producto = addProductoToDB(request.POST,request.FILES)

            messages.success(request, f"Producto {producto.cod} {producto.name} creado!")
            
            return redirect('editproductos')

    else:

        return redirect('viewproductos')

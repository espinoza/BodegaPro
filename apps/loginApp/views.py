from apps.mantenedorApp.models import Area
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import User
from apps.bodegaproAdminApp.models import ProxyUser
#from apps.rdcAdminApp.views import addProxy0ToDB
import bcrypt
from django.contrib import messages

DATE_FORMAT = "%Y-%m-%d"
SESSION_KEYS = [
    'id',
    'name',
    'is_active',
]


#SESSION
def resetSession(request):
    for key in SESSION_KEYS:
        if key in request.session:
            del request.session[key]

def addSession(request,user):
    request.session["id"] = user.id
    request.session["name"] = f"{user.name1}"
    request.session["is_active"] = user.is_active

#CRUD

def updateUserOnDB(user_id,user_data):
    user = User.objects.get(id = user_id)
    if "email" in user_data:
        user.email = user_data["email"]
    if "name1" in user_data:
        user.name1 = user_data["name1"]
    if "name2" in user_data:
        user.name2 = user_data["name2"]
    if "last_name1" in user_data:
        user.last_name1 = user_data["last_name1"]
    if "last_name2" in user_data:
        user.last_name2 = user_data["last_name2"]
    if "password" in user_data:
        user.password = passEncryptDecoded(user_data["password"])
    if "is_active" in user_data:
        user.is_active = user_data["is_active"]
    user.save()

def addToDB(user_data):
    user = User.objects.create(
        email = user_data['email'],
        name1 = user_data['name1'],
        #name2 = user_data['name2'],
        last_name1 = user_data['last_name1'],
        #last_name2 = user_data['last_name2'],
        password = passEncryptDecoded(user_data['password']),
    )
    return user

def getNumOfUsersDB():
    return User.objects.all().count()

def addProxy0ToDB(user,isAdmin = False):
    #adds Proxy when the user is created [use updateProxyOnDB for the rest of fields]
    proxy_user = ProxyUser.objects.create(
        user = user,
        alias = user.name1[:25].lower(),
        is_admin = isAdmin,
    )
    return proxy_user.id

def updateProxyOnDB(id_user, proxy_data):

    proxy_user = User.objects.get(id = id_user).more_info
    data_keys = ['alias','area','banco','banco_tipo_cuenta','banco_num_cuenta','rut','next_num_rdc','is_admin']
    for key in data_keys:
        if key in proxy_data:
            if key in ['alias','banco_num_cuenta']:
                setattr(proxy_user, key, proxy_data[key])
            elif key == "is_admin":
                if proxy_data[key] == "false":
                    setattr(proxy_user, key, False)
                else:
                    setattr(proxy_user, key, True)
                    #de pasada desasociar todos los permisos...
                    removeAllPermisos(id_user)
            elif key == 'rut':
                setattr(proxy_user, key, utils_rut.peinar_rut(proxy_data[key]))
            elif key == 'next_num_rdc':
                setattr(proxy_user, key, int(proxy_data[key]))
            else:
                if key == 'banco':
                    instance = Banco.objects.get(id = int(proxy_data[key]))
                elif key == 'banco_tipo_cuenta':
                    instance = TipoCuenta.objects.get(id = int(proxy_data[key]))
                elif key == 'area':
                    instance = Area.objects.get(id = int(proxy_data[key]))
                setattr(proxy_user, key, instance)
            #proxy_user[key] = proxy_data[key]
    proxy_user.save()

def removeAllPermisos(id_user):
    user = User.objects.get(id = id_user)
    user.areas_para_solicitar.clear()
    user.areas_para_autorizar.clear()
    user.areas_para_ejecutar.clear()


#MISC FUNCTIONS
def passEncryptDecoded(passwd):
    return bcrypt.hashpw(passwd.encode(),bcrypt.gensalt()).decode()

#ROUTES

def gotoLogin(request):

    if "id" in request.session:
        return showSuccess(request)

    elif request.method == 'POST': #esto para evitar que se entre directo a esta ruta
            
            errors = User.objects.login_validator(request.POST)
            
            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value)

                    context = {
                        'email' : request.POST['email'],
                        'password' : request.POST['password']
                    }

                return render(request,'login.html',context)

            else:

                user = User.objects.get(email = request.POST["email"])

                addSession(request,user)

                return showSuccess(request)

    return render(request,'login.html') #GET method, i.e. first time in login


def showSuccess(request):

    #user has an id and is active on DB!
    if "id" in request.session and request.session['is_active']:

        user = User.objects.get(id = request.session['id'])

        print(user.id)

        if user.isAdmin: #or user.puedeAutorizar or user.puedePagar:
            return redirect('dashboard', id_user=0, tipo='activemov')
        else: #user.puedeRendir:
            return redirect('dashboard', id_user=user.id, tipo='activemov')

    else:

        if not request.session['is_active']:
            user = User.objects.get(id = request.session['id'])
            messages.error(request, f"Usuario {user.name1} {user.name2[:1]} {user.last_name1} no está activo!")

        return redirect('signin')


def gotoRegister(request):

    if "id" in request.session: #en caso de entrar directo, usuario logeado se va al success
        return showSuccess(request)

    if request.method == 'POST': #esto para evitar que se entre directo a esta ruta
        errors = User.objects.user_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value) 

            context = {
                'email' : request.POST['email'],
                'name1' : request.POST['name1'],
                #'name2' : request.POST['name2'],
                'last_name1' : request.POST['last_name1'],
                #'last_name2' : request.POST['last_name2'],
                'password' : request.POST['password'],
                'confirm_password' : request.POST['confirm_password'],
            }
            
            return render(request,'register.html',context) #go back to "register" keeping data

        else:

            #Create User
            user = addToDB(request.POST) #necesariamente va con email, name1, name2, last_name1, last_name2, password
            #Create ProxyUser
            #check if first user (must be Admin)
            addProxy0ToDB(user,getNumOfUsersDB() == 1)

            messages.success(request, f"Usuario {user.full_name} creado!")
            
            addSession(request,user)

            return showSuccess(request)
    
    return render(request,'register.html') #Es GET (primera entrada)

def signOut(request):
    resetSession(request)
    return redirect('signin')

def checkEmail(request):

    print('cheqcking mail')

    if "id" in request.POST and int(request.POST["id"]) > 0:
        errors = User.objects.email_validator(request.POST["email"],"register",request.POST["id"])
    else:
        errors = User.objects.email_validator(request.POST["email"],"register")

    return JsonResponse(errors)
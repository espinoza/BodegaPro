
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import ProxyUser
from apps.loginApp.models import User, UserAutoriza, UserEjecuta, UserSolicita
from apps.loginApp.views import addToDB as addUserToDB, removePermisosTipoMov
from apps.loginApp.views import addProxy0ToDB, updateProxyOnDB, updateUserOnDB
from apps.mantenedorApp.models import Area, TipoMov
from django.contrib import messages

#MISC

#CRUD

def getTablaPermisos(id_user):

    areas = Area.objects.filter(is_active = True).order_by('pos')
    tipos_mov = TipoMov.objects.filter(is_active = True).order_by('pos')

    #Dict de dicts con clave tipoMov: Dict = { 'area_name','area_id', ['user_rinde','user_autoriza','user_paga']=True o False}

    tablaPermisos = {}

    for tipo_mov in tipos_mov:

        tipoMov = []

        for area in areas:
            miDict = {
                'area_id': area.id,
                'area_name': area.name,
                'user_solicita' : len(area.userstipomov_que_solicitan.filter(user__id=id_user,tipo_mov__id = tipo_mov.id)) > 0,
                'user_autoriza' : len(area.userstipomov_que_autorizan.filter(user__id=id_user,tipo_mov__id = tipo_mov.id)) > 0,
                'user_ejecuta' : len(area.userstipomov_que_ejecutan.filter(user__id=id_user,tipo_mov__id = tipo_mov.id)) > 0,
            }
            tipoMov.append(miDict)
        
        tablaPermisos[tipo_mov.id] = tipoMov


    return tablaPermisos

def savePermisos(post_data,id_user):

    user = User.objects.get(id = id_user)

    try:
        tipo_mov = TipoMov.objects.get(id = int(post_data['id_tipo_mov']))
    except:
        return False
 
    removePermisosTipoMov(user.id,tipo_mov)

    for key in post_data:

        if key[0].isnumeric() and int(key[-1]) == tipo_mov.id:

            solicita = int(post_data[key][0])
            autoriza = int(post_data[key][1])
            ejecuta = int(post_data[key][2])
            id_area = int(key.split('-')[0])  

            print(f'guardando {key}, id_area {id_area}')

            area = Area.objects.get(id = id_area)
            if solicita == 1:
                print(f'solicita area {area.name}, tipo_mov {tipo_mov.name}')
                UserSolicita.objects.create(
                    tipo_mov=tipo_mov,
                    user=user,
                    area=area
                )
            if autoriza == 1:
                UserAutoriza.objects.create(
                    tipo_mov=tipo_mov,
                    user=user,
                    area=area
                )
            if ejecuta == 1:
                UserEjecuta.objects.create(
                    tipo_mov=tipo_mov,
                    user=user,
                    area=area
                )

    return tipo_mov.name


#ROUTES

def gotoDashUsuarios(request):

    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')
        
    user = User.objects.get(id = request.session['id'])

    users = User.objects.all()

    context = {
        'user' : user,
        'users' : users,
    }

    return render(request, "userdashboard.html",context)

def viewUser(request,id_user):
    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    users = User.objects.filter(id = id_user)
    if len(users) == 0:
        return redirect('usuarios')

    user = User.objects.get(id = request.session['id']) #se requiere para armar menúbar (al menos)

    context = {
        'user_view' : users[0],
        'user' : user,
        'goBack' : 'users',
    }

    return render(request,"viewuser.html",context)

def newUser(request):

    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    user = User.objects.get(id = request.session["id"])
    if not user.isAdmin:
        return redirect('usuarios') 

    context = {
        'tipo' : 'create_user',
        'user' : user,
        'goBack' : 'users',
    }

    if request.method == 'POST': #esto para evitar que se entre directo a esta ruta
        
        errors = User.objects.user_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value) 

            context.update({
                'email' : request.POST['email'],
                'name1' : request.POST['name1'],
                #'name2' : request.POST['name2'],
                'last_name1' : request.POST['last_name1'],
                #'last_name2' : request.POST['last_name2'],
                'password' : request.POST['password'],
                'confirm_password' : request.POST['confirm_password'],
            })

        else:

            user = addUserToDB(request.POST)
            addProxy0ToDB(user,False)
            messages.success(request, f"Usuario {user.full_name} creado!")
    
    return render(request,'register.html',context)


def editUser(request,id_user):
    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    users = User.objects.filter(id = id_user)
    if len(users) == 0:
        return redirect('usuarios')

    return renderUser(request, users[0])


def updateUser(request): 

    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    logged_user = User.objects.get(id = request.session["id"])
    isAdmin = logged_user.isAdmin

    users = User.objects.filter(id = int(request.POST["id"]))
    if len(users) == 0:
        return redirect('usuarios') 

    user_to_update = users[0]

    if (not isAdmin) and ( int(request.POST["id"]) != request.session["id"] ):
        return redirect('usuarios') 
    
    tipo = request.POST["tipo"] #tipo: datagral, pass, banco, admin
    
    if tipo == "datagral":

        stError = False

        errors = User.objects.datagral_validator(request.POST)
        if len(errors) > 0:
            stError = True
            for key, value in errors.items():
                messages.error(request, value)

        if stError:        
            user_to_update.name1 = request.POST["name1"]
            #user_to_update.name2 = request.POST["name2"]
            user_to_update.last_name1 = request.POST["last_name1"]
            #user_to_update.last_name2 = request.POST["last_name2"]
            user_to_update.email = request.POST["email"]

            return renderUser(request,user_to_update)
    
        else:

            updateUserOnDB(user_to_update.id,request.POST)

            messages.success(request, f"Información actualizada para {user_to_update.full_name}!")

            return redirect("edituser",id_user = user_to_update.id)


    elif tipo == "pass":

        errors = User.objects.password_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)

            return renderUser(request,user_to_update) #do not put password...

        else:

            user_data = {
                'password' : request.POST["password"]
            }
            updateUserOnDB(user_to_update.id,user_data)

            messages.success(request, f"Contraseña actualizada para {user_to_update.full_name}!")

            return redirect("edituser",id_user = user_to_update.id)


    elif tipo == 'admin':

        stError = False

        errors = ProxyUser.objects.admin_validator(request.POST)
        if len(errors) > 0:
            stError = True
            for key, value in errors.items():
                messages.error(request, value)


        if stError:        
            
            user_to_update.more_info.alias = request.POST["alias"]
            
            if 'area' in request.POST:
                try:
                    user_to_update.more_info.area = Area.objects.get(id = int(request.POST["area"]))
                except:
                    pass
            
            try:
                if request.POST['is_admin'] == 'false':
                    user_to_update.more_info.is_admin = False
                else:
                    user_to_update.more_info.is_admin = True
            except:
                pass

            return renderUser(request,user_to_update)
    
        else:

            updateProxyOnDB(user_to_update.id,request.POST)

            messages.success(request, f"Datos adicionales actualizados para {user_to_update.full_name}!")

            return redirect("edituser",id_user = user_to_update.id)

    else:

        return redirect("dashboard")



def renderUser(request,user_edit):

    context = {
        'user' : User.objects.get(id = request.session['id']),
        'user_edit' : user_edit,
        'areas' : Area.objects.filter(is_active = True),
        'goBack' : 'users',
    }

    return render(request,"edituser.html",context)


def permisosUser(request,id_user, id_tipo_mov):
    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    try:
        user_edit = User.objects.get(id = id_user)
        user = User.objects.get(id = request.session['id'])
    except:
        return redirect('usuarios')

    if not user.isAdmin or user_edit.isAdmin:
        return redirect('usuarios')

    tipos_mov = TipoMov.objects.filter(is_active = True).order_by('pos')
    if int(id_tipo_mov) == 0:
        try:
            id_tipo_mov = tipos_mov[0].id
        except:
            pass


    context = {
        'user' : user,
        'user_edit' : user_edit,
        'tabla_permisos' : getTablaPermisos(id_user), #conseguir areas_que_rinde, autoriza, paga
        'tipos_mov' : tipos_mov,
        'id_tipo_mov' : id_tipo_mov,
        'goBack' : 'users',
    }

    return render(request,"permisos.html",context)

def savePermisosUser(request,id_user):
    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')

    try:
        user = User.objects.get(id = request.session['id'])
        user_edit = User.objects.get(id = id_user)
    except:
        return redirect('usuarios')  

    if not user.isAdmin or user_edit.isAdmin:
        return redirect('usuarios')  

    if request.method == "POST":

        print(request.POST)
        tipo_mov_txt = savePermisos(request.POST,id_user)

        messages.success(request, f"Permisos guardados ({ tipo_mov_txt })!")

        return redirect('permisosuser',id_user = id_user, id_tipo_mov=request.POST['id_tipo_mov'])

    else:

        return redirect('usuarios')


def toggleUser(request):
    if 'id' not in request.session or not request.session['is_active']:
        return redirect('signin')
    
    if User.objects.get(id = request.session['id']).isAdmin:

        users = User.objects.filter(id = request.POST['id'])
        if len(users) > 0:

            user_to_toggle = users[0]

            if request.POST['is_active'] == 'false':
                is_active = False
            else:
                is_active = True

            user_to_toggle.is_active = is_active
            user_to_toggle.save()

            print(f"toggle: {user_to_toggle.is_active}")

            response = {
                'status' : 'OK',
            }
            
        else:
            
            response = {
                'status' : "Usuario no encontrado!"
            }
            
        return JsonResponse(response)

    else:

        return redirect('usuarios')
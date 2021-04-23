
from django.urls import path
from . import views

urlpatterns = [
    #rdcadmin/...
    path('users', views.gotoDashUsuarios, name='usuarios'),
    path('users/new', views.newUser, name='newuser'),
    path('users/view/<int:id_user>', views.viewUser, name='viewuser'),
    path('users/edit/<int:id_user>', views.editUser, name='edituser'),
    path('users/edit/update',views.updateUser, name="update_data"), #tipo: password, datagral, admin, banco
    path('user/permisos/<int:id_user>', views.permisosUser, name='permisosuser'),
    path('user/permisos/<int:id_user>/save', views.savePermisosUser, name='savepermisos'),
    path('user/activar',views.toggleUser,name='toggleuseractivar'), #AJAX
    path('user/desactivar',views.toggleUser,name='toggleuserdesactivar'), #AJAX
]
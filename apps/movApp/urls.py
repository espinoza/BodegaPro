
from django.urls import path
from . import views

urlpatterns = [
    #rdc/...
    path('<int:id_user>/<str:tipo>', views.gotoDashboard, name='dashboard'), #id_user: id_user o '0:all' - tipo: 'allmov','activemov'
    path('requestNew', views.requestNewMov, name='request_new_mov'), # url de prueba
    path('new', views.createNewMov, name='create_new_mov'), # url de prueba
    path('<int:id_mov_encabezado>', views.gotoMov, name='goto_mov')
]
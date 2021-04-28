
from django.urls import path
from . import views

urlpatterns = [
    #rdc/...
    path('<int:id_user>/<str:tipo>', views.gotoDashboard, name='dashboard'), #id_user: id_user o '0:all' - tipo: 'allmov','activemov'
    path('requestNew', views.requestNewMov, name='request_new_mov'),
    path('new', views.createNewMov, name='create_new_mov'),
    path('view/<int:id_mov_encabezado>/', views.gotoMov, name='goto_mov'),
    path('solicitud/<int:id_mov_encabezado>/', views.solicitud, name='solicitud'),
    path('solicitud_ok/<int:id_mov_encabezado>/', views.solicitar_cancelar, name='solicitud_ok'),
]

from django.urls import path
from . import views

urlpatterns = [
    #rdc/...
    path('<int:id_user>/<str:tipo>', views.gotoDashboard, name='dashboard'), #id_user: id_user o '0:all' - tipo: 'allmov','activemov'

]
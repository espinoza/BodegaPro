# Create your views here.

from django.urls import path
from . import views

urlpatterns = [
    #rdc/...
    path('', views.gotoProductos, name='productos'),

]
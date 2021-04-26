# Create your views here.

from django.urls import path
from . import views

urlpatterns = [
    #rdc/...
    path('view', views.gotoProductos, name='viewproductos'),
    path('edit', views.editProductos, name='editproductos'),
    path('new',views.newProduct, name='newproduct' )
]
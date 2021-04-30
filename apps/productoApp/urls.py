# Create your views here.

from django.urls import path
from . import views

urlpatterns = [
    # rdc/...
    path('view', views.gotoProductos, name='viewproductos'),
    path('edit', views.editProductos, name='editproductos'),
    path('new', views.newProduct, name='newproduct'),
    path('grafico', views.Grafico, name='grafico'),
    path('item/activar', views.toggleItemProducto,
         name='toggleitemprodactivar'),  # AJAX
    path('item/desactivar', views.toggleItemProducto,
         name='toggleitemproddesactivar'),  # AJAX
    path('item/update', views.updateProduct, name="updateproducto"),  # AJAX
    path('get/filter', views.getFilteredProducts, name="productfilter"),  # AJAX

]

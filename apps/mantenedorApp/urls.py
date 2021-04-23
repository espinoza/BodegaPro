
from django.urls import path
from . import views

urlpatterns = [
    #mantenedor/...
    path('<str:tabla_name>', views.gotoMantenedor, name='mantenedor'),
    path('tabla/load',views.loadTabla, name = 'loadtabla'), #AJAX
    path('tabla/item/activar',views.toggleItemTabla, name = 'toggleitemtablaactivar'), #AJAX
    path('tabla/item/desactivar',views.toggleItemTabla, name = 'toggleitemtabladesactivar'), #AJAX
    path('tabla/item/add',views.newItemTabla, name='newitemtabla'), #AJAX
    path('tabla/item/update',views.updateItemTabla, name='updateitemtabla'), #AJAX
]
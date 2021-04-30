
from django.urls import path
from . import views

urlpatterns = [
    # rdc/...
    # id_user: id_user o '0:all' - tipo: 'allmov','activemov'
    path('<int:id_user>/<str:tipo>',
         views.gotoDashboard, name='dashboard'),
    path('requestNew',
         views.requestNewMov, name='request_new_mov'),
    path('new',
         views.createNewMov, name='create_new_mov'),
    path('view/<int:id_mov_encabezado>/',
         views.gotoMov, name='goto_mov'),
    path('solicitud/<int:id_mov_encabezado>/',
         views.solicitud, name='solicitud'),
    path('autorizacion/<int:id_mov_encabezado>/',
         views.autorizacion, name='autorizacion'),
    path('ejecucion/<int:id_mov_encabezado>/',
         views.ejecucion, name='ejecucion'),
    path('view/<int:id_mov_encabezado>/eliminarItem',
         views.eliminarItem, name='delete_item'),
    path('solicitud/<int:id_mov_encabezado>/item/delete',
         views.ajaxDelItem, name='ajax_delete_item'), #AJAX
    path('view/<int:id_mov_encabezado>/item/edit',
         views.ajaxEditItem, name='ajax_edit_item'), #AJAX
    path('view/<int:id_mov_encabezado>/editarItem',
         views.editarItem, name='edit_item'),
    path('view/<int:id_mov_encabezado>/cambiarEstado',
         views.cambiarEstado, name='change_status'),
    path('PDF/<int:id_mov_encabezado>/',
         views.sacarPDF, name='generar_pdf'),
    path('PDF/stock/',
         views.sacarPDFstock, name='generar_pdf_stock'),
    path('PDF/SinStock/',
         views.sacarPDFSinstock, name='generar_pdf_sin_stock'),
    path('harry/<int:id_mov_encabezado>/',
         views.modificando_stock, name="modificando_stock"),
]

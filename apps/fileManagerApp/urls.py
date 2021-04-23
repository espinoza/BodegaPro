
from django.urls import path
from . import views

urlpatterns = [
    #filemanager/... nothing yet...
    path('files',views.showUploadFile,name = 'files'),
    path('files/upload',views.uploadFile,name = 'uploadfile'),
]
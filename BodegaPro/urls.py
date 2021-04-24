"""BodegaPro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('apps.master.urls')),
    path('users/', include('apps.loginApp.urls')),
    path('mantenedor/', include('apps.mantenedorApp.urls')),
    path('movs/', include('apps.movApp.urls')),
    path('productos/', include('apps.productoApp.urls')),
    path('bodegapro/admin/', include('apps.bodegaproAdminApp.urls')),
    path('filemanager/', include('apps.fileManagerApp.urls')),
    path('admin/', admin.site.urls),
]

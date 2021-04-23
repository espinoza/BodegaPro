
from django.urls import path
from . import views

urlpatterns = [
    #users/...
    path('', views.gotoIndex, name='index'),
]
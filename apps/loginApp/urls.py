
from django.urls import path
from . import views

urlpatterns = [
    #users/...
    path('', views.gotoLogin, name='signin'),
    path('register',views.gotoRegister, name='register'),
    path('login/signout',views.signOut, name='signout'),
    path('register/checkEmail',views.checkEmail),
]
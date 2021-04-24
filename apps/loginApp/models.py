
from apps.mantenedorApp.models import Area, TipoMov
from django.db import models
from django.db.models.fields import CharField, DateTimeField, EmailField
import bcrypt
import re  # Regex

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class UserManager(models.Manager):

    #    def areasQue(self, tipo: str, tipo_mov, user_id): #tipo: 'solicita', 'autoriza', 'ejecuta'
    #        if tipo[:3] == 'sol':
    #            return self.get(id = user_id).areas_que_solicita.filter(tipo_mov)
    #        elif tipo[:3] == 'aut':
    #            return self.get(id = user_id).areas_que_autoriza.filter(tipo_mov)
    #        elif tipo[:3] == 'eje':
    #            return self.get(id = user_id).areas_que_ejecuta.filter(tipo_mov)

    def chk_pass(self, email, passwd):
        user = self.filter(email=email)

        if user:
            return bcrypt.checkpw(passwd.encode(), user[0].password.encode())

        return False

    def email_exists(self, email, exclude_id=0):
        if exclude_id == 0:
            return self.filter(email=email)
        else:
            return self.filter(email=email).exclude(id=exclude_id)

    def email_validator(self, email, tipo, exclude_id=0):  # 'tipo: register o login'
        errors = {}
        if email == "":
            errors["email"] = "Email requerido!"
        # probar si un campo coincide con el patrón
        elif not EMAIL_REGEX.match(email):
            errors["email"] = "Email inválido!"
        elif tipo == "register":
            if self.email_exists(email, exclude_id):
                errors["email"] = "Este email ya existe en la aplicación!"

        return errors

    def login_validator(self, post_data):  # para el login
        errors = {}

        field_name = "email"
        field_value = post_data["email"]
        if field_value == "":
            errors[field_name] = "Email requerido!"

        # if not self.email_exists(field_value) or not self.chk_pass(post_data["password"]):
        # esta rutina chequea la existencia del mail...
        if not self.chk_pass(post_data["email"], post_data["password"]):
            errors[field_name] = "Error en email y/o contraseña!"

        return errors

    def datagral_validator(self, post_data):
        return self.user_validator(post_data, True, False)

    def password_validator(self, post_data):
        return self.user_validator(post_data, False, True)

    def user_validator(self, post_data, chkDataGral=True, chkPass=True):
        errors = {}

        if chkDataGral:

            field_name = "name1"
            field_value = post_data[field_name]
            if field_value == "":
                errors[field_name] = "Se requiere al menos el primer nombre!"
            elif len(field_value) < 2 or len(field_value) > 50:
                errors[field_name] = "El primer nombre debe estar entre 2 y 50 caracteres"

            field_name = "last_name1"
            field_value = post_data[field_name]
            if field_value == "":
                errors[field_name] = "Se requiere el apellido!"
            elif len(field_value) < 2 or len(field_value) > 50:
                errors[field_name] = "El primer apellido debe estar entre 2 y 50 caracteres"

            #field_name = "last_name2"
            #field_value = post_data[field_name]
            # if field_value == "":
            #    errors[field_name] = "Se requiere el segundo apellido!"
            # elif len(field_value)<2 or len(field_value)>50:
            #    errors[field_name] = "El segundo apellido debe estar entre 2 y 50 caracteres"

            field_name = "email"
            field_value = post_data[field_name]
            if "id" in post_data:
                email_errors = self.email_validator(
                    field_value, "register", exclude_id=post_data["id"])
            else:
                email_errors = self.email_validator(field_value, "register")
            if email_errors:
                errors[field_name] = email_errors["email"]

        if chkPass:
            field_name = "password"
            field_value = post_data[field_name]
            if field_value == "":
                errors[field_name] = "Se requiere una contraseña!"
            elif len(field_value) < 8 or len(field_value) > 50:
                errors[field_name] = "La contraseña debe tener al menos 8 caracteres."
            elif post_data['confirm_password'] == "":
                errors["confirm_password"] = "Por favor, confirmar contraseña!"
            elif field_value != post_data["confirm_password"]:
                errors["confirm_password"] = "La contraseña y su confirmación no cuadran. Corregir!"

        return errors


class User(models.Model):
    email = EmailField(max_length=100, unique=True)
    name1 = CharField(max_length=50)
    last_name1 = CharField(max_length=50)
    password = CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    #more_info - ProxyUser

    areas_para_solicitar = models.ManyToManyField(
        Area, through="UserSolicita", related_name="users_que_solicitan")
    areas_para_autorizar = models.ManyToManyField(
        Area, through="UserAutoriza", related_name="users_que_autorizan")
    areas_para_ejecutar = models.ManyToManyField(
        Area, through="UserEjecuta", related_name="users_que_ejecutan")

    #mis_mov - MovEncabezado
    #mov_autorizados - MovEstado
    #mov_pagados - MovEstado

    def __str__(self):
        return f"Usuario {self.name1} {self.last_name1}"
    objects = UserManager()

    @property
    def full_name(self):
        return f"{self.name1} {self.last_name1}"

    # @property
    def puedeSolicitar(self):
        return self.areas_para_solicitar.count() > 0

    # @property
    def puedeAutorizar(self):
        return self.areas_para_autorizar.count() > 0

    # @property
    def puedeEjecutar(self):
        return self.areas_para_ejecutar.count() > 0

    @property
    def isAdmin(self):
        return self.more_info.is_admin


class UserSolicita(models.Model):
    tipo_mov = models.ForeignKey(
        TipoMov, related_name="areausers_que_solicitan", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="areastipomov_donde_solicita", on_delete=models.CASCADE)
    area = models.ForeignKey(
        Area, related_name="userstipomov_que_solicitan", on_delete=models.CASCADE)


class UserAutoriza(models.Model):
    tipo_mov = models.ForeignKey(
        TipoMov, related_name="areausers_que_autorizan", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="areastipomov_donde_autoriza", on_delete=models.CASCADE)
    area = models.ForeignKey(
        Area, related_name="userstipomov_que_autorizan", on_delete=models.CASCADE)


class UserEjecuta(models.Model):
    tipo_mov = models.ForeignKey(
        TipoMov, related_name="areausers_que_ejecutan", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="areastipomov_donde_ejecuta", on_delete=models.CASCADE)
    area = models.ForeignKey(
        Area, related_name="userstipomov_que_ejecutan", on_delete=models.CASCADE)

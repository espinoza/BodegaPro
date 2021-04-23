
from django.db.models.fields.related import OneToOneField
from django.db import models
from django.db.models.fields import CharField, DateTimeField, IntegerField, PositiveSmallIntegerField, BooleanField

class MantenedorManager(models.Manager):

    def name_exists(self,name,exclude_id = 0):
        if exclude_id == 0:
            return self.filter(name = name)
        else:
            return self.filter(name = name).exclude(id = exclude_id)

    def mantenedor_validator(self,post_data,exclude_id = 0):
        errors = {}

        field_name = "name"
        field_value = post_data[field_name]
        if field_value == "":
            errors[field_name] = "Se requiere al menos la descripción del item!"
        elif len(field_value) > 80:
            errors[field_name] = "El item debe tener menos de 100 caracteres"
        elif self.name_exists(field_value,exclude_id):
            errors[field_name] = "La descripción ya existe!"

        field_name = "pos"
        field_value = post_data[field_name]
        if field_value == "":
            errors[field_name] = "La posición del ítem no puede ser omitida!"
        elif int(field_value) > 32000:
            errors[field_name] = "La posición máxima no puede superar 32000"

        return errors

class Area(models.Model):
    name = CharField(max_length=100)
    pos = PositiveSmallIntegerField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    #users_que_solicitan = models.ManyToManyField(User,related_name='areas_que_solicitan')
    #users_que_autorizan = models.ManyToManyField(User,related_name='areas_que_autorizan')
    #users_que_ejecutan = models.ManyToManyField(User,related_name='areas_que_ejecuta')
    
    objects = MantenedorManager()

class Estado(models.Model):
    name = CharField(max_length=100)
    pos = PositiveSmallIntegerField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects = MantenedorManager()


class Folio(models.Model):
    #tipo_mov - TipoMov
    num_folio = IntegerField()

class TipoMov(models.Model):
    name = CharField(max_length=100)
    pos = PositiveSmallIntegerField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    folio = OneToOneField(Folio,related_name="tipo_mov",null=True,on_delete=models.PROTECT)

    objects = MantenedorManager()


class TipoMedida(models.Model):
    #unidad_medida - UnidadMedida
    decimales = PositiveSmallIntegerField()

class UnidadMedida(models.Model):
    name = CharField(max_length=100)
    pos = PositiveSmallIntegerField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    tipo_medida = models.OneToOneField(TipoMedida,related_name="unidad_medida",null=True,on_delete=models.PROTECT)
    #productos - Producto

    objects = MantenedorManager()


class Familia(models.Model):
    name = CharField(max_length=100)
    pos = PositiveSmallIntegerField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    #productos - Producto

    objects = MantenedorManager()








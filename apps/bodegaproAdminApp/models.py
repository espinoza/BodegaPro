
from django.db.models.fields.related import ForeignKey
from apps.loginApp.models import User
from apps.mantenedorApp.models import Area, TipoMov
from django.db import models
from django.db.models.fields import BooleanField, DateTimeField

class ProxyUserManager(models.Manager):

    def exist_area(self,id_area):
        if len(Area.objects.filter(id = id_area)) > 0:
            return True
        return False

    def exist_alias(self,alias,id_user):
        if len(ProxyUser.objects.filter(alias = alias, user__is_active = True).exclude(id = id_user)) > 0:
            return True
        return False


    def admin_validator(self,post_data):
        errors = {}

        field_name = "alias"
        field_value = post_data[field_name]
        if field_value == "":
            errors[field_name] = "Se requiere un ALIAS"
        elif self.exist_alias(field_value,post_data['id']):
            errors[field_name] = "El alias ya existe. Cambiar."

        field_name = "area"
        if not field_name in post_data:
            errors[field_name] = "Elija un area para el usuario!"
        else:
            field_value = post_data[field_name]
            if not self.exist_area(int(field_value)):
                errors[field_name] = "Area no encontrada."

        return errors


class ProxyUser(models.Model):
    user = models.OneToOneField(User,related_name='more_info',on_delete=models.PROTECT)
    alias = models.CharField(max_length=25)
    area = models.ForeignKey(Area,related_name='users',on_delete=models.PROTECT,null=True)
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects = ProxyUserManager()







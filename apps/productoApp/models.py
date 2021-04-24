from django.db.models.fields.related import ForeignKey
from apps.mantenedorApp.models import Area, TipoMov, UnidadMedida, Familia
from django.db import models
from django.db.models.fields import BooleanField, CharField, IntegerField


class ProductoManager(models.Manager):

    pass


class Producto(models.Model):
    cod = IntegerField()
    name = CharField(max_length=100)
    img_url = CharField(null=True, max_length=300)
    unidad_medida = ForeignKey(
        UnidadMedida, related_name="productos", on_delete=models.PROTECT)
    familia = ForeignKey(Familia, related_name="productos",
                         on_delete=models.PROTECT)
    is_Active = BooleanField(default=True)

    def __str__(self):
        return f"Producto {self.name}"

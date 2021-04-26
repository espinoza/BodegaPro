from django.db.models.fields.related import ForeignKey
from apps.mantenedorApp.models import Area, TipoMov, UnidadMedida, Familia
from django.db import models
from django.db.models.fields import BooleanField, CharField, IntegerField


class ProductoManager(models.Manager):

    def is_valid_file_extension(self,file_data):
        if len(file_data) == 0:
            return False
        filename = file_data["img_url"].name.lower()
        if ".jpg" in filename or ".png" in filename or ".jpeg" in filename or ".gif" in filename:
            return True
        return False
        

    def cod_exist(self,cod):
        if len(self.filter(cod = cod)) > 0:
            return True
        return False

    def producto_validator(self, post_data):
        errors = {}

        print(post_data)

        field_name = "cod"
        field_value = post_data[field_name]
        if field_value == "":
            errors[field_name] = "Se requiere un código de 8 dígitos."

        try:
            valor = int(field_value)
            if valor < 10000000 or valor > 99999999:
                errors[field_name] = "Código fuera de rango. Debe tener sólo dígitos (8)."
            elif self.cod_exist(valor):
                errors[field_name] = "El código ya existe en el Maestro de Productos."
        except:
            errors[field_name] = "Formato de código inválido. Debe tener 8 dígitos!"


        field_name = "name"
        field_value = post_data[field_name]
        if field_value == "":
            errors[field_name] = "Se requiere la descripción del producto."
        elif len(field_value) <= 5 or len(field_value) > 100:
            errors[field_name] = "La descripción del producto debe tener entre 6 y 100 caracteres"

        field_name = "unidad_medida"
        if not field_name in post_data:
            errors[field_name] = "Especificar Unidad"
        else:
            try:
                field_value = post_data[field_name]
                unidad = int(field_value) #.id
                if len(UnidadMedida.objects.filter(id = unidad)) == 0:
                    errors[field_name] = "Unidad inválida"
            except:
                errors[field_name] = "Especificar Unidad"

        field_name = "familia"
        if not field_name in post_data:
            errors[field_name] = "Especificar Familia"
        else:
            try:
                field_value = post_data[field_name]
                familia = int(field_value) #.id
                if len(Familia.objects.filter(id = familia)) == 0:
                    errors[field_name] = "Familia inválida"
            except:
                errors[field_name] = "Especificar Familia"

        return errors
    


class Producto(models.Model):
    cod = IntegerField(unique=True)
    name = CharField(max_length=100)
    img_url = CharField(null=True, max_length=300)
    unidad_medida = ForeignKey(
        UnidadMedida, related_name="productos", on_delete=models.PROTECT)
    familia = ForeignKey(Familia, related_name="productos",
                         on_delete=models.PROTECT)
    is_active = BooleanField(default=True)

    #stock_data - STOCK (.cantidad, .monto_total)

    def __str__(self):
        return f"Producto {self.name}"

    objects = ProductoManager()

    @property
    def precio_unit(self):
        if self.stock_data.cantidad != 0:
            return round(self.stock_data.monto_total/self.stock_data.cantidad,1)
        else:
            return 0

    @property
    def cantidad(self):
        return self.stock_data.cantidad


    


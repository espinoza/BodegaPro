from apps.productoApp.models import Producto
from apps.loginApp.models import User
from apps.mantenedorApp.models import Area, Estado, TipoMov
from django.db import models
from django.db.models.fields import CharField, DateTimeField, IntegerField


class MovManager(models.Manager):

    pass
#    def rdc_motivo_validator(self,motivo):
#        errors = {}
#        if motivo == "":
#            errors['motivo'] = "Debe especificar el motivo de la RDC!"
#        elif len(motivo)<10 or len(motivo)>200:
#            errors['motivo'] = "El motivo de la RDC debe tener al menos 10 caracteres (max:200)"
#
#        return errors



class MovEncabezado(models.Model):
    area = models.ForeignKey(Area,related_name="movs_asociados",on_delete=models.PROTECT)
    tipo_mov = models.ForeignKey(TipoMov,related_name="movs_asociados",on_delete=models.PROTECT)
    folio = IntegerField()
    descripcion = CharField(max_length=200,default='')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    #mov_items - MovItem
    #mov_estados - MovEstado

    objects = MovManager()

    @property
    def estado(self):
        estados = self.mov_estados.all()
        if len(estados.filter(estado__name = 'EJECUTADO'))>0:
            return 'EJECUTADO'
        elif len(estados.filter(estado__name = 'CANCELADO'))>0:
            return 'CANCELADO'
        elif len(estados.filter(estado__name = 'NO AUTORIZADO'))>0:
            return 'NO AUTORIZADO'
        elif len(estados.filter(estado__name = 'AUTORIZADO'))>0:
            return 'AUTORIZADO'
        elif len(estados.filter(estado__name = 'SOLICITADO'))>0:
            return 'SOLICITADO'
        else:
            return 'CREADO'

    @property 
    def num_items_solicitado(self):
        n = 0
        for fila_det in self.mov_items.all():
            try:
                if abs(fila_det.cant_solicitada) > 0:
                    n+=1
            except:
                pass

        return n

    @property 
    def num_items_autorizado(self):
        n = 0
        for fila_det in self.mov_items.all():
            try:
                if abs(fila_det.cant_autorizada) > 0:
                    n+=1
            except:
                pass
        return n

    @property 
    def num_items_ejecutado(self):
        n = 0
        for fila_det in self.mov_items.all():
            try:
                if abs(fila_det.cant_ejecutada) > 0:
                    n+=1
            except:
                pass
        return n


    @property
    def monto_solicitado(self):
        monto = 0
        for fila_det in self.mov_items.all():
            try:
                monto += fila_det.monto_solicitado
            except:
                pass
        return monto

    @property
    def monto_autorizado(self):
        monto = 0
        for fila_det in self.mov_items.all():
            try:
                monto += fila_det.monto_autorizado
            except:
                pass
        return monto

    @property
    def monto_ejecutado(self):
        monto = 0
        for fila_det in self.mov_items.all():
            try:
                monto += fila_det.monto_ejecutado
            except:
                pass
        return monto

class MovItem(models.Model):
    mov_encabezado = models.ForeignKey(MovEncabezado,related_name='mov_items',on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto,related_name='movs_asociados',on_delete=models.PROTECT)
    cant_solicitada = models.FloatField()
    cant_autorizada = models.FloatField(null=True)
    cant_ejecutada = models.FloatField(null=True)
    precio_unit = models.FloatField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    @property
    def monto_solicitado(self):
        try:
            monto = self.cant_solicitada*self.precio_unit
        except:
            monto = 0
        return monto

    @property
    def monto_autorizado(self):
        try:
            monto = self.cant_autorizada*self.precio_unit
        except:
            monto = 0
        return monto

    @property
    def monto_ejecutado(self):
        try:
            monto = self.cant_ejecutada*self.precio_unit
        except:
            monto = 0
        return monto


class MovEstado(models.Model):
    mov_encabezado = models.ForeignKey(MovEncabezado,related_name='mov_estados',on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado,related_name="movs_asociados",on_delete=models.PROTECT)
    user = models.ForeignKey(User,related_name='movs_asociados',on_delete=models.PROTECT)
    nota = models.CharField(max_length=200)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class Stock(models.Model):
    producto = models.OneToOneField(Producto,related_name="stock_data",on_delete=models.CASCADE)
    cantidad = models.FloatField(default=0)
    monto_total = models.FloatField(default=0)

    def __str__(self):
        return f"{self.producto.name} Cant:{self.cantidad} Monto Total ${self.monto_total}"


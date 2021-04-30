from django import forms
from apps.mantenedorApp.models import Area, TipoMov
from apps.movApp.models import MovEncabezado
from apps.mantenedorApp.models import Estado


class CleanModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class EditMovEncabezadoForm(forms.Form):

    descripcion = forms.CharField(max_length=200)
    area = CleanModelChoiceField(
        queryset=Area.objects.filter(is_active=True).order_by('pos')
    )

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion")
        if len(descripcion) < 5:
            raise forms.ValidationError("Descripción muy corta")
        return descripcion


class NewMovEncabezadoForm(EditMovEncabezadoForm):

    tipo_mov = CleanModelChoiceField(
        queryset=TipoMov.objects.filter(is_active=True).order_by('pos')
    )

    def clean(self):
        cleaned_data = super(NewMovEncabezadoForm, self).clean()
        estado_creado = Estado.objects.filter(name="CREADO")
        if estado_creado and estado_creado[0].is_active:
            return cleaned_data
        raise forms.ValidationError(
            "En estos momentos no está permitido crear solicitudes"
        )


class AddProductoToMovForm(forms.Form):

    cod = forms.IntegerField(required=False)
    name = forms.CharField(max_length=100, required=False)
    cant_solicitada = forms.FloatField()

    def clean(self):
        cleaned_data = super(AddProductoToMovForm, self).clean()
        cod = cleaned_data.get("cod")
        name = cleaned_data.get("name")
        if cod is None and len(name) == 0:
            print("raise 1")
            raise forms.ValidationError(
                "Debe ingresar código o nombre de producto"
            )
        #if cod is not None and len(name) > 0:
        #    print("raise 2")
        #    raise forms.ValidationError(
        #        "Debe ingresar código o nombre, pero no ambos"
        #    )
        cant_solicitada = cleaned_data.get("cant_solicitada")
        if cant_solicitada == 0:
            print("raise 3")
            raise forms.ValidationError(
                "Debe ingresar un valor mayor que cero"
            )
        return cleaned_data


class AddProductoEntradaToMovForm(AddProductoToMovForm):

    precio_unit = forms.FloatField()

    def clean(self):
        cleaned_data = super(AddProductoEntradaToMovForm, self).clean()
        precio_unit = cleaned_data.get("precio_unit")
        if precio_unit < 0:
            raise forms.ValidationError(
                "Debe ingresar un valor mayor que cero"
            )
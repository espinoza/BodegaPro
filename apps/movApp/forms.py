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
        queryset=Area.objects.filter(is_active=True),
    )

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion")
        if len(descripcion) < 5:
            raise forms.ValidationError("Descripción muy corta")
        return descripcion


class NewMovEncabezadoForm(EditMovEncabezadoForm):

    tipo_mov = CleanModelChoiceField(
        queryset=TipoMov.objects.filter(is_active=True)
    )

    def clean(self):
        cleaned_data = super(NewMovEncabezadoForm, self).clean()
        estado_creado = Estado.objects.filter(name="CREADO")
        if estado_creado and estado_creado[0].is_active:
            return cleaned_data
        raise forms.ValidationError(
            "En estos momentos no está permitido crear solicitudes"
        )

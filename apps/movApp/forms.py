from django import forms
from apps.mantenedorApp.models import Area, TipoMov
from apps.movApp.models import MovEncabezado


class CleanModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class NewMovForm(forms.ModelForm):

    area = CleanModelChoiceField(
        queryset=Area.objects.filter(is_active=True),
    )
    tipo_mov = CleanModelChoiceField(
        queryset=TipoMov.objects.filter(is_active=True)
    )

    class Meta:
        model = MovEncabezado
        fields = ['descripcion']


    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion")
        if len(descripcion) < 5:
            raise forms.ValidationError("Descripción muy corta")
        return descripcion

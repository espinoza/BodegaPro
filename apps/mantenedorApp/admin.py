from django.contrib import admin
from .models import *
# Register your models here.
show_full_result_count = False

admin.site.register(Area)
admin.site.register(Estado)
admin.site.register(Folio)
admin.site.register(TipoMov)
admin.site.register(TipoMedida)
admin.site.register(UnidadMedida)
admin.site.register(Familia)

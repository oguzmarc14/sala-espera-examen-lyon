from django.contrib import admin
from .models import Sala 

# Register your models here.
@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad','ubicacion','creado_el','actualizado_el')
    search_fields = ('nombre','ubicacion')
    list_filter = ('capacidad', 'ubicacion')
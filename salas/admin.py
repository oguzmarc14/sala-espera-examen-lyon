from django.contrib import admin
from .models import Sala 

# Register your models here.
@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad','ubicacion','created_at','updated_at')
    search_fields = ('nombre','ubicacion')
    list_filter = ('capacidad', 'ubicacion')
from django.db import models
from django.core.validators import MinValueValidator

class Sala(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    capacidad = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
# Create your models here.

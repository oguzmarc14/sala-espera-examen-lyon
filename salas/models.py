from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Sala(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    capacidad = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


# Create your models here.


class Reserva(models.Model):
    sala = models.ForeignKey("Sala", on_delete=models.CASCADE, related_name="reservas")
    titulo = models.CharField(max_length=100)
    nombre_contacto = models.CharField(max_length=100)
    email_contacto = models.EmailField()
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=20,
        choices=[
            ("pendiente", "Pendiente"),
            ("confirmada", "Confirmada"),
            ("cancelada", "Cancelada"),
        ],
        default="pendiente",
    )
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fecha", "hora_inicio"]
        indexes = [models.Index(fields=["sala", "fecha"])]
    
    def clean(self):
        #horario valido
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de incio debe de ser menor que la hora de fin")
        #validacion de misma sala con fecha
        qs = Reserva.objects.filter(sala=self.sala, fecha=self.fecha)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.filter(hora_inicio__lt=self.hora_fin, hora_fin__gt=self.hora_inicio).exists():
            raise ValidationError("El horarrio se empalma con otra reserva que ya existe")
        
    def save(self, *args, **kwargs):
        self.full_clean()  # corre clean() y valida campos
        return super().save(*args, **kwargs)
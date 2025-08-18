from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


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
        """
        Reglas:
        - Rango válido: hora_inicio < hora_fin (bordes abiertos [inicio, fin)).
        - No permitir solapes en misma sala y fecha.
        """
        # 1) Horario válido
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError(
                "La hora de inicio debe ser menor que la hora de fin."
            )

        # 2) Mismas sala y fecha (usa índice compuesto para eficiencia)
        # Obtiene todas las reservas que ocurren en la misma sala y fecha que la actual
        qs = Reserva.objects.filter(sala=self.sala, fecha=self.fecha)

        # Evita auto-colisión si estamos editando (ya tiene pk)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        # 3) Solape: inicio_existente < fin_nueva  y  fin_existente > inicio_nueva
        if qs.filter(
            hora_inicio__lt=self.hora_fin, hora_fin__gt=self.hora_inicio
        ).exists():
            raise ValidationError(
                "El horario se empalma con otra reserva que ya existe."
            )

        # dutacion de 2hrs
        dt_inicio = datetime.combine(self.fecha, self.hora_inicio)
        dt_fin = datetime.combine(self.fecha, self.hora_fin)
        if dt_fin - dt_inicio > timedelta(hours=2):
            raise ValidationError("La duracion maxima es de 2 horas")

    def save(self, *args, **kwargs):
        # Ejecuta validaciones del modelo siempre (admin, DRF, etc.)
        self.full_clean()
        return super().save(*args, **kwargs)

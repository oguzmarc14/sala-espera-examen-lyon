# salas/serializers.py
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import datetime, timedelta
from .models import Sala, Reserva


class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = "__all__"


class ReservaSerializer(serializers.ModelSerializer):
    # detalle embebido de la sala (solo lectura)
    sala_detalle = SalaSerializer(source="sala", read_only=True)

    class Meta:
        model = Reserva
        fields = [
            "id", "sala", "sala_detalle", "titulo", "nombre_contacto", "email_contacto",
            "fecha", "hora_inicio", "hora_fin", "estado", "notas",
            "creado_en", "actualizado_en",
        ]
        read_only_fields = ["creado_en", "actualizado_en"]

    def validate(self, data):
        # horario de inicio menor a horario final 
        hi = data.get("hora_inicio") or getattr(self.instance, "hora_inicio", None)
        hf = data.get("hora_fin") or getattr(self.instance, "hora_fin", None)
        fecha = data.get("fecha") or getattr(self.instance, "fecha", None)
        sala = data.get("sala") or getattr(self.instance, "sala", None)

        # 1) Horario válido
        if hi and hf and hi >= hf:
            raise serializers.ValidationError("hora_inicio debe ser menor que hora_fin.")

        # 2) Duración máxima 2h
        if fecha and hi and hf:
            duracion = datetime.combine(fecha, hf) - datetime.combine(fecha, hi)
            if duracion > timedelta(hours=2):
                raise serializers.ValidationError("La duración máxima de una reserva es de 2 horas.")

        # 3) Anti-solapamiento (intervalo semiabierto [inicio, fin))
        if sala and fecha and hi and hf:
            qs = Reserva.objects.filter(sala=sala, fecha=fecha)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.filter(hora_inicio__lt=hf, hora_fin__gt=hi).exists():
                raise serializers.ValidationError("El horario se empalma con otra reserva existente.")

        return data

    # Convertimos ValidationError de Django (modelo.full_clean) a serializers.ValidationError (HTTP 400)
    def create(self, validated_data):
        instance = Reserva(**validated_data)
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            # Soporta e.message_dict (por campo) o e.messages (lista)
            raise serializers.ValidationError(e.message_dict or e.messages)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict or e.messages)
        instance.save()
        return instance

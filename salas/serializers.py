from .models import Sala, Reserva
from rest_framework import serializers

class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = '__all__'
        
class ReservaSerializer(serializers.ModelSerializer):
    sala_detalle = SalaSerializer(source="sala", read_only="true")
    
    class Meta:
        model = Reserva
        fields = [
            "id", "sala", "sala_detalle", "titulo", "nombre_contacto", "email_contacto",
            "fecha", "hora_inicio", "hora_fin", "estado", "notas",
            "creado_en", "actualizado_en",
        ]
        read_only_fields = ["creado_en", "actualizado_en"]

    def validate(self, data):
        # Refuerzo de horario (además del clean() del modelo)
        hi = data.get("hora_inicio") or getattr(self.instance, "hora_inicio", None)
        hf = data.get("hora_fin") or getattr(self.instance, "hora_fin", None)
        if hi and hf and hi >= hf:
            raise serializers.ValidationError("hora_inicio debe ser menor que hora_fin.")

        # Refuerzo de solapamiento
        sala = data.get("sala") or getattr(self.instance, "sala", None)
        fecha = data.get("fecha") or getattr(self.instance, "fecha", None)
        if sala and fecha and hi and hf:
            qs = Reserva.objects.filter(sala=sala, fecha=fecha)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.filter(hora_inicio__lt=hf, hora_fin__gt=hi).exists():
                raise serializers.ValidationError("El horario se empalma con otra reserva existente.")
        return data
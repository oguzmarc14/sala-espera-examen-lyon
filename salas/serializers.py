from .models import Sala
from rest_framework import serializers

class SalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = '__all__'
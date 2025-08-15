from rest_framework import viewsets 
from .models import Sala
from .serializers import SalaSerializer, ReservaSerializer
from rest_framework.permissions import AllowAny

# Create your views here.
class SalaViewSet(viewsets.ModelViewSet):
    queryset = Sala.objects.all().order_by("nombre")
    serializer_class = SalaSerializer
    permission_classes = [AllowAny]
    
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        qs = super().get_queryset()
        sala_id = self.request.query_params.get("sala")
        fecha = self.request.query_params.get("fecha")  # YYYY-MM-DD
        if sala_id:
            qs = qs.filter(sala_id=sala_id)
        if fecha:
            qs = qs.filter(fecha=fecha)
        return qs
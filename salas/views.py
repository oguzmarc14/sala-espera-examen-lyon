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
    

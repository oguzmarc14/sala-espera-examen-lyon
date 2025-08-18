from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Sala, Reserva
from .serializers import SalaSerializer, ReservaSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class SalaViewSet(viewsets.ModelViewSet):
    queryset = Sala.objects.all().order_by("nombre")
    serializer_class = SalaSerializer
    permission_classes = [AllowAny]


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = (
        Reserva.objects.select_related("sala").all().order_by("fecha", "hora_inicio")
    )
    serializer_class = ReservaSerializer
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["sala", "fecha", "estado"]
    ordering_fields = ["fecha", "hora_inicio", "hora_fin", "creado_en"]
    search_fields = ["titulo", "nombre_contacto", "email_contacto"]

    def get_queryset(self):
        qs = super().get_queryset()
        sala_id = self.request.query_params.get("sala")
        fecha = self.request.query_params.get("fecha")  # YYYY-MM-DD
        if sala_id:
            qs = qs.filter(sala_id=sala_id)
        if fecha:
            qs = qs.filter(fecha=fecha)
        return qs

    @action(detail=True, methods=["post"])
    def liberar(self, request, pk=None):
        # cancelar manualmente una reservaa pasa de estado a cancelada
        reserva = self.get_object()
        if reserva.estado == "cancelada":
            return Response({"detail": "La reserva ya esta cancelada."}, status=400)
        type(reserva).objects.filter(pk=reserva.pk).update(estado="cancelada")
        reserva.refresh_from_db()
        return Response(self.get_serializer(reserva).data, status=status.HTTP_200_OK)

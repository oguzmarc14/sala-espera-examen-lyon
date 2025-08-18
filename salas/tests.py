from django.test import TestCase

# Create your tests here.

# salas/tests.py
from datetime import date, time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Sala, Reserva


class ReservaAPITests(APITestCase):
    def setUp(self):
        #sala de prueba 
        self.sala = Sala.objects.create(nombre="Sala Test", capacidad=10, ubicacion="A")

    def _payload(self, **overrides):
        base = dict(
            sala=self.sala.id,
            titulo="Reunión",
            nombre_contacto="Juan",
            email_contacto="juan@example.com",
            fecha=str(date(2025, 8, 20)),
            hora_inicio="10:00",
            hora_fin="11:00",
            estado="pendiente",
            notas="",
        )
        base.update(overrides)
        return base

    def test_crear_reserva_valida(self):
        #validando una reserva normal
        url = reverse("reserva-list")
        resp = self.client.post(url, self._payload(), format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["sala"], self.sala.id)
        self.assertEqual(resp.data["hora_inicio"], "10:00:00")
        self.assertEqual(resp.data["hora_fin"], "11:00:00")

    def test_anti_solapamiento_misma_sala_misma_fecha(self):
        url = reverse("reserva-list")
        # reserva inicial 10:00-11:00
        self.client.post(url, self._payload(), format="json")
        # intento solape 10:30-10:45
        resp = self.client.post(
            url, self._payload(hora_inicio="10:30", hora_fin="10:45"), format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("empalma", str(resp.data).lower())

    def test_back_to_back_es_permitido(self):
        url = reverse("reserva-list")
        # 10:00-11:00
        r1 = self.client.post(url, self._payload(), format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        # 11:00-12:00 (toca borde pero no solapa)
        r2 = self.client.post(
            url, self._payload(hora_inicio="11:00", hora_fin="12:00"), format="json"
        )
        self.assertEqual(r2.status_code, status.HTTP_201_CREATED)

    def test_duracion_mayor_a_2h_rechazada(self):
        url = reverse("reserva-list")
        resp = self.client.post(
            url, self._payload(hora_inicio="08:00", hora_fin="11:00"), format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("2 horas", str(resp.data))

    def test_liberar_cancela_reserva(self):
        # Creamos una reserva larga (>2h) para comprobar que liberar la cancela igual
        url = reverse("reserva-list")
        crear = self.client.post(
            url, self._payload(hora_inicio="08:00", hora_fin="11:00"), format="json"
        )
        self.assertEqual(
            crear.status_code, status.HTTP_400_BAD_REQUEST
        )  # bloqueada por serializer

        # Creamos una valida para poder liberarla
        crear_ok = self.client.post(url, self._payload(), format="json")
        self.assertEqual(crear_ok.status_code, status.HTTP_201_CREATED)
        rid = crear_ok.data["id"]

        # POST /api/reservas/{id}/liberar/
        url_liberar = reverse("reserva-liberar", args=[rid])
        resp = self.client.post(url_liberar, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["estado"], "cancelada")

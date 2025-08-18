from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from salas.views import SalaViewSet, ReservaViewSet

router = DefaultRouter()
router.register(r"salas", SalaViewSet, basename="sala")
router.register(r"reservas", ReservaViewSet, basename="reserva")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]

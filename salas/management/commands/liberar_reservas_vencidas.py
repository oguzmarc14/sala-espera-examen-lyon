from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from salas.models import Reserva

class Command(BaseCommand):
    help = "Libera reservas cuyo horario ya venció"

    def handle(self, *args, **kwargs):
        now = timezone.localtime()
        hoy = now.date()
        hora = now.time()

        vencidas = Reserva.objects.filter(
            estado="pendiente"
        ).filter(
            Q(fecha__lt=hoy) | Q(fecha=hoy, hora_fin__lte=hora)
        )

        updated = vencidas.update(estado="cancelada")
        self.stdout.write(self.style.SUCCESS(f"Reservas liberadas: {updated}"))

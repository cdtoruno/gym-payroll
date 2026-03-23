from django.db import models
from apps.employees.models import Employee


class LateArrival(models.Model):
    """
    Registro de llegadas tarde por empleado.
    Cada registro representa 1 llegada tarde y el descuento
    que se aplicará en la quincena correspondiente.
    """
    class Meta:
        db_table            = "late_arrivals"
        verbose_name        = "Llegada tarde"
        verbose_name_plural = "Llegadas tarde"
        ordering            = ["-fecha"]
        # No se puede registrar dos llegadas tarde el mismo día
        unique_together     = [("employee", "fecha")]

    employee     = models.ForeignKey(
        Employee, on_delete=models.CASCADE,
        related_name="late_arrivals", verbose_name="Empleado"
    )
    fecha        = models.DateField("Fecha")
    hora_llegada = models.TimeField("Hora de llegada real")
    minutos_tarde = models.PositiveIntegerField(
        "Minutos de retraso", default=0
    )
    descuento    = models.DecimalField(
        "Descuento aplicado", max_digits=10, decimal_places=2, default=0
    )
    period       = models.IntegerField(
        "Quincena",
        choices=[(1, "Primera quincena (1–15)"), (2, "Segunda quincena (16–fin)")],
    )
    notas        = models.TextField("Notas", blank=True, default="")
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} — {self.fecha} — C${self.descuento}"

@property
def horas_tarde(self):
    """
    Redondea hacia arriba al siguiente hora completa.
    1–60 min tarde  → 1 hora
    61–120 min tarde → 2 horas
    etc.
    """
    if self.minutos_tarde <= 0:
        return 0
    import math
    return math.ceil(self.minutos_tarde / 60)
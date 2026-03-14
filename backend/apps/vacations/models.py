from datetime import date as date_type
from django.db import models
from apps.employees.models import Employee


class Vacation(models.Model):
    class Meta:
        db_table            = "vacations"
        verbose_name        = "Vacaciones"
        verbose_name_plural = "Vacaciones"

    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE,
        related_name="vacation", verbose_name="Empleado"
    )
    dias_disponibles = models.PositiveIntegerField("Días disponibles", default=2)
    dias_falta_q1    = models.PositiveIntegerField("Faltas en Q1", default=0)
    dias_falta_q2    = models.PositiveIntegerField("Faltas en Q2", default=0)
    mes_vigente      = models.DateField("Mes vigente", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Vacaciones — {self.employee.name}"

    @property
    def dias_falta_pendiente(self):
        return self.dias_falta_q1

    @property
    def dias_a_pagar(self):
        return max(0, self.dias_disponibles - self.dias_falta_q1)

    @property
    def monto_vacaciones(self):
        pago_por_dia = self.employee.salary_base / 12
        return round(float(self.dias_a_pagar * pago_por_dia), 2)

    def iniciar_nuevo_mes(self, year: int, month: int):
        mes_actual = date_type(year, month, 1)
        if self.mes_vigente and self.mes_vigente >= mes_actual:
            return
        self.dias_falta_q1    = self.dias_falta_q2
        self.dias_falta_q2    = 0
        self.dias_disponibles = 2
        self.mes_vigente      = mes_actual
        self.save(update_fields=[
            "dias_falta_q1", "dias_falta_q2",
            "dias_disponibles", "mes_vigente", "updated_at"
        ])

    def registrar_falta(self, fecha: date_type) -> bool:
        """
        Registra 1 día de falta según la fecha.
        Sin límite de faltas — el pago mínimo es C$0.
        - Días 1–15 (Q1) → afecta Q1 del mes actual
        - Días 16–31 (Q2) → afecta Q1 del mes siguiente
        Siempre retorna True.
        """
        if fecha.day <= 15:
            self.dias_falta_q1 += 1
            self.save(update_fields=["dias_falta_q1", "updated_at"])
        else:
            self.dias_falta_q2 += 1
            self.save(update_fields=["dias_falta_q2", "updated_at"])
        return True


class VacationAbsence(models.Model):
    """
    Registro histórico de cada falta por vacaciones.
    Permite saber exactamente qué día y en qué mes faltó cada empleado.
    """
    class Meta:
        db_table            = "vacation_absences"
        verbose_name        = "Falta de vacaciones"
        verbose_name_plural = "Faltas de vacaciones"
        ordering            = ["-fecha"]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE,
        related_name="vacation_absences", verbose_name="Empleado"
    )
    fecha     = models.DateField("Fecha de falta")
    motivo    = models.CharField("Motivo", max_length=200, default="Falta por vacaciones")
    es_q1     = models.BooleanField("¿Es Q1?", default=True)
    mes_afectado = models.DateField(
        "Mes afectado",
        help_text="Mes en que se aplica el descuento"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} — {self.fecha}"
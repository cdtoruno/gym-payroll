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

    # Días disponibles del mes vigente
    dias_disponibles = models.PositiveIntegerField(
        "Días disponibles", default=2
    )

    # Faltas en Q1 (días 1-15) → afectan el Q1 del MES ACTUAL
    dias_falta_q1 = models.PositiveIntegerField(
        "Faltas en Q1 (afectan Q1 actual)", default=0
    )

    # Faltas en Q2 (días 16-31) → afectan el Q1 del MES SIGUIENTE
    dias_falta_q2 = models.PositiveIntegerField(
        "Faltas en Q2 (afectan Q1 siguiente)", default=0
    )

    # Mes en que se acreditaron los días actuales
    mes_vigente = models.DateField(
        "Mes vigente", null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Vacaciones — {self.employee.name}"

    @property
    def dias_falta_pendiente(self):
        """Total de faltas que afectan el Q1 actual."""
        return self.dias_falta_q1

    @property
    def dias_a_pagar(self):
        """
        Días reales a pagar en el Q1 actual.
        Descuenta las faltas de Q1 del mes vigente.
        """
        return max(0, self.dias_disponibles - self.dias_falta_q1)

    @property
    def monto_vacaciones(self):
        """Monto a pagar en Q1 según días a pagar."""
        pago_por_dia = self.employee.salary_base / 12
        return round(float(self.dias_a_pagar * pago_por_dia), 2)

    def iniciar_nuevo_mes(self, year: int, month: int):
        """
        Llamado al INICIO de la generación del Q1 de un nuevo mes.
        - Acredita 2 días frescos
        - Transfiere las faltas de Q2 del mes anterior a Q1 del mes actual
        - Resetea las faltas de Q2

        Solo actúa si es un mes diferente al mes_vigente.
        """
        mes_actual = date_type(year, month, 1)

        # Si ya se inició este mes, no hacer nada
        if self.mes_vigente and self.mes_vigente >= mes_actual:
            return

        # Las faltas de Q2 del mes anterior pasan a Q1 del mes actual
        self.dias_falta_q1  = self.dias_falta_q2
        self.dias_falta_q2  = 0
        self.dias_disponibles = 2
        self.mes_vigente    = mes_actual
        self.save(update_fields=[
            "dias_falta_q1", "dias_falta_q2",
            "dias_disponibles", "mes_vigente", "updated_at"
        ])

    def registrar_falta(self, fecha: date_type) -> bool:
        """
        Registra 1 día de falta según la fecha:
        - Días 1–15  (Q1) → afecta el Q1 del mes actual
        - Días 16–31 (Q2) → afecta el Q1 del mes siguiente

        Retorna True si se registró, False si ya alcanzó el límite.
        """
        if fecha.day <= 15:
            # Falta en Q1 → afecta Q1 actual
            if self.dias_falta_q1 < self.dias_disponibles:
                self.dias_falta_q1 += 1
                self.save(update_fields=["dias_falta_q1", "updated_at"])
                return True
        else:
            # Falta en Q2 → afecta Q1 siguiente
            total_faltas = self.dias_falta_q1 + self.dias_falta_q2
            if total_faltas < self.dias_disponibles:
                self.dias_falta_q2 += 1
                self.save(update_fields=["dias_falta_q2", "updated_at"])
                return True

        return False
from django.db import models
from apps.employees.models import Employee


class PayrollRecord(models.Model):

    class PeriodChoices(models.IntegerChoices):
        FIRST  = 1, "Primera quincena (1–15)"
        SECOND = 2, "Segunda quincena (16–fin)"

    class Meta:
        db_table            = "payroll"
        verbose_name        = "Nómina"
        verbose_name_plural = "Nóminas"
        ordering            = ["-date", "-period"]
        unique_together     = [("employee", "date", "period")]

    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT,
        related_name="payroll_records", verbose_name="Empleado"
    )
    date            = models.DateField("Fecha de nómina")
    period          = models.IntegerField("Período", choices=PeriodChoices.choices)
    dias_laborados  = models.PositiveIntegerField("Días laborados", default=15)

    # ── Ingresos ──────────────────────────────────────────────────────────
    salary_base      = models.DecimalField("Salario ordinario",  max_digits=10, decimal_places=2)
    vacation_payment = models.DecimalField("Vacaciones",         max_digits=10, decimal_places=2, default=0)
    viatico          = models.DecimalField("Viático",            max_digits=10, decimal_places=2, default=0)

    # ── Deducciones ───────────────────────────────────────────────────────
    otras_deducciones  = models.DecimalField("Otras deducciones",        max_digits=10, decimal_places=2, default=0)
    prestamo_adelanto  = models.DecimalField("Deduc. Préstamo/Adelanto",  max_digits=10, decimal_places=2, default=0)
    descuento_faltas   = models.DecimalField(
        "Descuento por faltas",
        max_digits=10, decimal_places=2, default=0,
        help_text="Días extra faltados × (salario ÷ 15). Se aplica en Q2."
    )

    # ── Totales ───────────────────────────────────────────────────────────
    sub_total = models.DecimalField("Sub-total devengado", max_digits=10, decimal_places=2, default=0)
    total     = models.DecimalField("Total devengado",     max_digits=10, decimal_places=2)

    notes      = models.TextField("Notas", blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        tag = "Q1" if self.period == 1 else "Q2"
        return f"{self.employee.name} — {self.date:%Y-%m} {tag} — C${self.total}"
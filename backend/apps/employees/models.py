from django.db import models


class Employee(models.Model):
    class Meta:
        db_table            = "employees"
        verbose_name        = "Empleado"
        verbose_name_plural = "Empleados"
        ordering            = ["name"]

    name        = models.CharField("Nombre completo", max_length=150)
    cedula      = models.CharField("Cédula", max_length=20, blank=True, default="")
    phone       = models.CharField("Teléfono", max_length=20, blank=True, default="")
    position    = models.CharField("Cargo", max_length=100)
    salary_base = models.DecimalField(
        "Salario base quincenal", max_digits=10, decimal_places=2
    )
    hire_date   = models.DateField("Fecha de contratación")
    active      = models.BooleanField("Activo", default=True)

    # ── Horario ───────────────────────────────────────────────────────────────
    hora_entrada  = models.TimeField("Hora de entrada", null=True, blank=True)
    hora_salida   = models.TimeField("Hora de salida",  null=True, blank=True)
    horas_por_dia = models.DecimalField(
        "Horas laborales por día",
        max_digits=4, decimal_places=1,
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} — {self.position}"

    @property
    def valor_por_hora(self):
        """Cuánto vale 1 hora de trabajo para este empleado."""
        if not self.horas_por_dia or self.horas_por_dia == 0:
            return 0
        return round(float(self.salary_base) / 15 / float(self.horas_por_dia), 2)
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

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} — {self.position}"
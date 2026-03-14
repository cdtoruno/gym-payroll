from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vacations", "0003_update_falta_fields"),
        ("employees", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="VacationAbsence",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vacation_absences",
                        to="employees.employee",
                        verbose_name="Empleado",
                    ),
                ),
                ("fecha",        models.DateField(verbose_name="Fecha de falta")),
                ("motivo",       models.CharField(default="Falta por vacaciones", max_length=200, verbose_name="Motivo")),
                ("es_q1",        models.BooleanField(default=True, verbose_name="¿Es Q1?")),
                ("mes_afectado", models.DateField(help_text="Mes en que se aplica el descuento", verbose_name="Mes afectado")),
                ("created_at",   models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Falta de vacaciones",
                "verbose_name_plural": "Faltas de vacaciones",
                "db_table": "vacation_absences",
                "ordering": ["-fecha"],
            },
        ),
    ]
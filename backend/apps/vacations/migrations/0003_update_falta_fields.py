from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vacations", "0002_update_vacation_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vacation",
            name="dias_falta_pendiente",
        ),
        migrations.AddField(
            model_name="vacation",
            name="dias_falta_q1",
            field=models.PositiveIntegerField(
                default=0,
                verbose_name="Faltas en Q1 (afectan Q1 actual)"
            ),
        ),
        migrations.AddField(
            model_name="vacation",
            name="dias_falta_q2",
            field=models.PositiveIntegerField(
                default=0,
                verbose_name="Faltas en Q2 (afectan Q1 siguiente)"
            ),
        ),
        migrations.AddField(
            model_name="vacation",
            name="mes_vigente",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="Mes vigente"
            ),
        ),
    ]
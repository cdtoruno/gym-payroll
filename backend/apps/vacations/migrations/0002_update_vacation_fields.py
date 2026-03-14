from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vacations", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vacation",
            name="total_days",
        ),
        migrations.RemoveField(
            model_name="vacation",
            name="used_days",
        ),
        migrations.RemoveField(
            model_name="vacation",
            name="vacation_payment",
        ),
        migrations.AddField(
            model_name="vacation",
            name="dias_disponibles",
            field=models.PositiveIntegerField(default=2, verbose_name="Días disponibles"),
        ),
        migrations.AddField(
            model_name="vacation",
            name="dias_falta_pendiente",
            field=models.PositiveIntegerField(
                default=0,
                verbose_name="Días de falta pendiente (se descuenta en siguiente Q1)"
            ),
        ),
    ]
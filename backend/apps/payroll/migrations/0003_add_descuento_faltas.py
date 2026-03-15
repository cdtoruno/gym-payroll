from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="payrollrecord",
            name="descuento_faltas",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Días extra faltados × (salario ÷ 15). Se aplica en Q2.",
                max_digits=10,
                verbose_name="Descuento por faltas",
            ),
        ),
    ]
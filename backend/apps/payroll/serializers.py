from decimal import Decimal
from rest_framework import serializers
from apps.vacations.models import VacationAbsence
from .models import PayrollRecord


class PayrollRecordSerializer(serializers.ModelSerializer):
    employee_name    = serializers.CharField(source="employee.name",   read_only=True)
    employee_cedula  = serializers.CharField(source="employee.cedula", read_only=True)
    period_label     = serializers.SerializerMethodField()
    dias_laborados   = serializers.SerializerMethodField()

    class Meta:
        model  = PayrollRecord
        fields = [
            "id", "employee", "employee_name", "employee_cedula",
            "date", "period", "period_label", "dias_laborados",
            "salary_base", "vacation_payment", "viatico",
            "otras_deducciones", "prestamo_adelanto", "descuento_faltas",
            "sub_total", "total",
            "notes", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "salary_base", "vacation_payment", "descuento_faltas",
            "sub_total", "total", "created_at", "updated_at",
        ]

    def get_period_label(self, obj):
        return obj.get_period_display()

    def get_dias_laborados(self, obj):
        """
        Días laborados reales = días registrados - faltas del mes.
        Las faltas son independientes del descuento de vacaciones.
        """
        faltas = VacationAbsence.objects.filter(
            employee     = obj.employee,
            fecha__year  = obj.date.year,
            fecha__month = obj.date.month,
        ).count()
        return max(0, obj.dias_laborados - faltas)


class PayrollItemSerializer(serializers.Serializer):
    employee_id       = serializers.IntegerField()
    viatico           = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"))
    otras_deducciones = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"))
    prestamo_adelanto = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"))
    notes             = serializers.CharField(required=False, allow_blank=True, default="")


class BulkPayrollSerializer(serializers.Serializer):
    date    = serializers.DateField()
    period  = serializers.ChoiceField(choices=[1, 2])
    items   = serializers.ListField(
        child=PayrollItemSerializer(),
        min_length=1
    )


class GeneratePayrollSerializer(serializers.Serializer):
    employee          = serializers.IntegerField()
    date              = serializers.DateField()
    period            = serializers.ChoiceField(choices=[1, 2])
    dias_laborados    = serializers.IntegerField(default=15, min_value=1, max_value=15)
    viatico           = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"))
    otras_deducciones = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"))
    prestamo_adelanto = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"))
    notes             = serializers.CharField(required=False, allow_blank=True, default="")
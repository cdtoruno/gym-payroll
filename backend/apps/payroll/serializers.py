from decimal import Decimal
from rest_framework import serializers
from .models import PayrollRecord


class PayrollRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_cedula = serializers.CharField(source="employee.cedula", read_only=True)
    period_label  = serializers.SerializerMethodField()

    class Meta:
        model  = PayrollRecord
        fields = [
            "id", "employee", "employee_name", "employee_cedula",
            "date", "period", "period_label", "dias_laborados",
            # Ingresos
            "salary_base", "vacation_payment", "viatico",
            # Deducciones
            "otras_deducciones", "prestamo_adelanto",
            # Totales
            "sub_total", "total",
            "notes", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "salary_base", "vacation_payment",
            "sub_total", "total", "created_at", "updated_at",
        ]

    def get_period_label(self, obj):
        return obj.get_period_display()


class GeneratePayrollSerializer(serializers.Serializer):
    """Serializador de entrada para POST /api/payroll/generate/"""
    employee          = serializers.IntegerField()
    date              = serializers.DateField()
    period            = serializers.ChoiceField(choices=[1, 2])
    dias_laborados    = serializers.IntegerField(default=15, min_value=1, max_value=15)
    viatico           = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"))
    otras_deducciones = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"))
    prestamo_adelanto = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"))
    notes             = serializers.CharField(required=False, allow_blank=True, default="")
from rest_framework import serializers
from datetime import datetime
from .models import LateArrival
from apps.employees.models import Employee


class LateArrivalSerializer(serializers.ModelSerializer):
    employee_name    = serializers.CharField(source="employee.name", read_only=True)
    employee_position = serializers.CharField(source="employee.position", read_only=True)
    horas_tarde      = serializers.IntegerField(read_only=True)
    period_label     = serializers.SerializerMethodField()

    class Meta:
        model  = LateArrival
        fields = [
            "id", "employee", "employee_name", "employee_position",
            "fecha", "hora_llegada", "minutos_tarde", "horas_tarde",
            "descuento", "period", "period_label",
            "notas", "created_at",
        ]
        read_only_fields = ["id", "descuento", "period", "created_at"]

    def get_period_label(self, obj):
        return obj.get_period_display()

    def validate(self, data):
        employee     = data.get("employee")
        fecha        = data.get("fecha")
        hora_llegada = data.get("hora_llegada")

        # ── Verificar que el empleado tiene horario configurado ───────────
        if not employee.hora_entrada:
            raise serializers.ValidationError(
                f"{employee.name} no tiene horario configurado."
            )

        # ── Verificar duplicado ───────────────────────────────────────────
        qs = LateArrival.objects.filter(employee=employee, fecha=fecha)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"{employee.name} ya tiene una llegada tarde registrada "
                f"el {fecha}."
            )

        # ── Calcular minutos tarde ────────────────────────────────────────
        hora_entrada_dt  = datetime.combine(fecha, employee.hora_entrada)
        hora_llegada_dt  = datetime.combine(fecha, hora_llegada)
        diferencia       = hora_llegada_dt - hora_entrada_dt
        minutos_tarde    = int(diferencia.total_seconds() / 60)

        if minutos_tarde <= 0:
            raise serializers.ValidationError(
                f"{employee.name} no llegó tarde el {fecha}. "
                f"Su hora de entrada es {employee.hora_entrada}."
            )

        data["minutos_tarde"] = minutos_tarde

        # ── Calcular descuento (1 hora completa aunque sea 1 min tarde) ───
        data["descuento"] = employee.valor_por_hora

        # ── Determinar quincena ───────────────────────────────────────────
        data["period"] = 1 if fecha.day <= 15 else 2

        return data


class RegisterLateArrivalSerializer(serializers.Serializer):
    """Serializer de entrada para registrar llegada tarde."""
    employee_id  = serializers.IntegerField()
    fecha        = serializers.DateField()
    hora_llegada = serializers.TimeField()
    notas        = serializers.CharField(required=False, allow_blank=True, default="")
from rest_framework import serializers
from .models import Vacation


class VacationSerializer(serializers.ModelSerializer):
    employee_name        = serializers.CharField(source="employee.name", read_only=True)
    dias_a_pagar         = serializers.IntegerField(read_only=True)
    monto_vacaciones     = serializers.FloatField(read_only=True)

    class Meta:
        model  = Vacation
        fields = [
            "id", "employee", "employee_name",
            "dias_disponibles", "dias_falta_pendiente",
            "dias_a_pagar", "monto_vacaciones",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_dias_falta_pendiente(self, value):
        """No puede haber más faltas que días disponibles."""
        dias_disponibles = self.initial_data.get(
            "dias_disponibles",
            getattr(self.instance, "dias_disponibles", 2)
        )
        if value > int(dias_disponibles):
            raise serializers.ValidationError(
                "Los días de falta no pueden superar los días disponibles."
            )
        return value


class RegistrarFaltaSerializer(serializers.Serializer):
    """Serializer de entrada para POST /api/vacations/{id}/falta/"""
    employee_id = serializers.IntegerField()
    fecha       = serializers.DateField()
    motivo      = serializers.CharField(
        required=False, allow_blank=True, default="Falta por vacaciones"
    )
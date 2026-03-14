from rest_framework import serializers
from .models import Vacation, VacationAbsence


class VacationSerializer(serializers.ModelSerializer):
    employee_name         = serializers.CharField(source="employee.name", read_only=True)
    dias_a_pagar          = serializers.IntegerField(read_only=True)
    monto_vacaciones      = serializers.FloatField(read_only=True)

    class Meta:
        model  = Vacation
        fields = [
            "id", "employee", "employee_name",
            "dias_disponibles", "dias_falta_q1", "dias_falta_q2",
            "dias_a_pagar", "monto_vacaciones", "mes_vigente",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        disponibles = data.get(
            "dias_disponibles",
            getattr(self.instance, "dias_disponibles", 2)
        )
        q1 = data.get("dias_falta_q1", getattr(self.instance, "dias_falta_q1", 0))
        q2 = data.get("dias_falta_q2", getattr(self.instance, "dias_falta_q2", 0))

        if q1 > disponibles:
            raise serializers.ValidationError(
                {"dias_falta_q1": "Las faltas Q1 no pueden superar los días disponibles."}
            )
        if q2 > disponibles:
            raise serializers.ValidationError(
                {"dias_falta_q2": "Las faltas Q2 no pueden superar los días disponibles."}
            )
        return data


class VacationAbsenceSerializer(serializers.ModelSerializer):
    employee_name    = serializers.CharField(source="employee.name", read_only=True)
    mes_afectado_str = serializers.SerializerMethodField()
    quincena_label   = serializers.SerializerMethodField()

    class Meta:
        model  = VacationAbsence
        fields = [
            "id", "employee", "employee_name",
            "fecha", "motivo", "es_q1",
            "mes_afectado", "mes_afectado_str",
            "quincena_label", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_mes_afectado_str(self, obj):
        meses = [
            "", "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return f"{meses[obj.mes_afectado.month]} {obj.mes_afectado.year}"

    def get_quincena_label(self, obj):
        return "Q1 (1–15)" if obj.es_q1 else "Q2 (16–fin)"


class RegistrarFaltaSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    fecha       = serializers.DateField()
    motivo      = serializers.CharField(
        required=False, allow_blank=True, default="Falta por vacaciones"
    )
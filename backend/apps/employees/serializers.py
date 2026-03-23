from rest_framework import serializers
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    valor_por_hora = serializers.FloatField(read_only=True)

    class Meta:
        model  = Employee
        fields = [
            "id", "name", "cedula", "phone", "position",
            "salary_base", "hire_date", "active",
            "hora_entrada", "hora_salida", "horas_por_dia",
            "valor_por_hora",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_salary_base(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El salario base debe ser mayor a cero."
            )
        return value

    def validate_cedula(self, value):
        if value:
            qs = Employee.objects.filter(cedula=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ya existe un empleado con esta cédula."
                )
        return value

    def validate(self, data):
        hora_entrada  = data.get("hora_entrada")
        hora_salida   = data.get("hora_salida")
        horas_por_dia = data.get("horas_por_dia")

        if hora_entrada and hora_salida and not horas_por_dia:
            raise serializers.ValidationError(
                {"horas_por_dia": "Debes indicar las horas laborales por día."}
            )
        return data
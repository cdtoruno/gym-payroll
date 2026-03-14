from rest_framework import serializers
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Employee
        fields = [
            "id", "name", "cedula", "phone", "position",
            "salary_base", "hire_date", "active",
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
            # Verificar que no exista otra cédula igual
            qs = Employee.objects.filter(cedula=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ya existe un empleado con esta cédula."
                )
        return value
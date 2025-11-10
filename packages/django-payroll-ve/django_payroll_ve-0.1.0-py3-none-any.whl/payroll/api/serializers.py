from rest_framework import serializers
from payroll.models.employee import Employee
from payroll.models.component import PayComponent
from payroll.models.payslip import Payslip, PayslipLine


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


class PayComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayComponent
        fields = "__all__"


class PayslipLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayslipLine
        fields = ["component", "amount"]


class PayslipCreateSerializer(serializers.ModelSerializer):
    lines = PayslipLineSerializer(many=True)
    class Meta:
        model = Payslip
        fields = ["company", "employee", "period", "date", "currency", "remarks", "lines"]
    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        ps = Payslip.objects.create(**validated_data)
        for l in lines:
            PayslipLine.objects.create(payslip=ps, **l)
        return ps
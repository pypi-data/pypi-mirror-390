from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import HttpResponse


from payroll.api.serializers import (
EmployeeSerializer, PayComponentSerializer,
PayslipCreateSerializer,
)
from payroll.models.payslip import Payslip
from payroll.posting.adapters import post_payslip
from payroll.conf import get as confget
from payroll.utils.pdf import render_payslip_pdf


class EmployeeListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = EmployeeSerializer(data=request.data); ser.is_valid(raise_exception=True); ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


class PayComponentListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = PayComponentSerializer(data=request.data); ser.is_valid(raise_exception=True); ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


class PayslipCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = PayslipCreateSerializer(data=request.data); ser.is_valid(raise_exception=True)
        ps = ser.save()
        if confget("AUTO_POST"):
            entry = post_payslip(ps)
            return Response({"payslip_id": ps.id, "journal_entry_id": entry.id}, status=status.HTTP_201_CREATED)
        return Response({"payslip_id": ps.id}, status=status.HTTP_201_CREATED)


class PayslipPDF(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        ps = Payslip.objects.select_related("employee", "company").get(pk=pk)
        pdf = render_payslip_pdf(ps, company=ps.company)
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f"inline; filename=payslip-{ps.employee.code}-{ps.period}.pdf"
        return resp
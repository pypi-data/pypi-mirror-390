from django.db import models
from decimal import Decimal

class Payslip(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    employee = models.ForeignKey("payroll.Employee", on_delete=models.CASCADE)
    period = models.CharField(max_length=16)  # e.g. 2025-11
    date = models.DateField()
    currency = models.CharField(max_length=3, default="INR")
    is_posted = models.BooleanField(default=False)
    journal_entry_id = models.IntegerField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ("company", "employee", "period")

class PayslipLine(models.Model):
    payslip = models.ForeignKey(Payslip, related_name="lines", on_delete=models.CASCADE)
    component = models.ForeignKey("payroll.PayComponent", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

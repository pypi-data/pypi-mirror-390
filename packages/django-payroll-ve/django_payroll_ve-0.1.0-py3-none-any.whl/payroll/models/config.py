from django.db import models
class PayrollAccountMapping(models.Model):
    company = models.OneToOneField("finacc.Company", on_delete=models.CASCADE)
    salary_expense = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="salary_expense_acc")
    salary_payable = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="salary_payable_acc")

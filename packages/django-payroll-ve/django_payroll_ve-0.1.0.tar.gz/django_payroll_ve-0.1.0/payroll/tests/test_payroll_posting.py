import pytest
from decimal import Decimal
from finacc.models.company import Company
from finacc.models.accounts import Account
from payroll.models.employee import Employee
from payroll.models.component import PayComponent
from payroll.models.config import PayrollAccountMapping
from payroll.models.payslip import Payslip, PayslipLine
from payroll.posting.adapters import post_payslip


@pytest.mark.django_db
def test_payslip_posts_to_finacc():
    c = Company.objects.create(name="ACME")
    emp = Employee.objects.create(company=c, code="E001", name="Alice", join_date="2024-01-01")
    exp = Account.objects.create(company=c, code="5100", name="Salary Expense", kind="expense", normal_balance="debit")
    pay = Account.objects.create(company=c, code="2300", name="Salary Payable", kind="liability", normal_balance="credit")
    comp_acc = exp
    PayrollAccountMapping.objects.create(company=c, salary_expense=exp, salary_payable=pay)
    pc_basic = PayComponent.objects.create(company=c, code="BASIC", name="Basic", type="earning", account=comp_acc)
    pc_pf = PayComponent.objects.create(company=c, code="PF", name="PF", type="deduction", account=pay)


    ps = Payslip.objects.create(company=c, employee=emp, period="2025-11", date="2025-11-30", currency="INR")
    PayslipLine.objects.create(payslip=ps, component=pc_basic, amount=Decimal("50000.00"))
    PayslipLine.objects.create(payslip=ps, component=pc_pf, amount=Decimal("1800.00"))


    entry = post_payslip(ps)
    assert entry.is_posted and ps.journal_entry_id == entry.id and ps.is_posted
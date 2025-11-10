from finacc.posting.rules import create_simple_entry
from finacc.posting.engine import post_entry
from decimal import Decimal
from payroll.models.payslip import Payslip
from payroll.models.config import PayrollAccountMapping

def post_payslip(payslip: Payslip):
    mapping = PayrollAccountMapping.objects.get(company=payslip.company)
    lines = []
    total_earn = Decimal("0.00")
    total_ded = Decimal("0.00")
    for line in payslip.lines.select_related("component"):
        if line.component.type == "earning":
            total_earn += line.amount
            lines.append({"account": line.component.account, "debit": line.amount, "credit": Decimal("0.00")})
        else:
            total_ded += line.amount
            lines.append({"account": line.component.account, "credit": line.amount, "debit": Decimal("0.00")})
    net = total_earn - total_ded
    lines.append({"account": mapping.salary_expense, "debit": total_earn, "credit": Decimal("0.00")})
    lines.append({"account": mapping.salary_payable, "credit": net, "debit": Decimal("0.00")})
    je = create_simple_entry(payslip.company, payslip.date, payslip.currency, f"Payroll {payslip.period}", lines)
    entry = post_entry(je)
    payslip.is_posted = True
    payslip.journal_entry_id = entry.id
    payslip.save(update_fields=["is_posted", "journal_entry_id"])
    return entry

from django.core.management.base import BaseCommand
from finacc.models.company import Company
from finacc.models.accounts import Account
from payroll.models.employee import Employee
from payroll.models.component import PayComponent
from payroll.models.config import PayrollAccountMapping


class Command(BaseCommand):
    help = "Create demo employees, components, and payroll account mapping"


def add_arguments(self, parser):
    parser.add_argument("--company", type=int, required=True)


def handle(self, *args, **opts):
    c = Company.objects.get(id=opts["company"])
    Employee.objects.get_or_create(company=c, code="E001", defaults={"name":"Alice", "join_date":"2024-01-01"})
    Employee.objects.get_or_create(company=c, code="E002", defaults={"name":"Bob", "join_date":"2024-06-01"})
    # Accounts by CoA code (adjust to your chart)
    def acc(code): return Account.objects.get(company=c, code=code)
    PayrollAccountMapping.objects.get_or_create(company=c, defaults={
    "salary_expense": acc("5100"),
    "salary_payable": acc("2300"),
    })
    PayComponent.objects.get_or_create(company=c, code="BASIC", defaults={"name":"Basic", "type":"earning", "account": acc("5100")})
    PayComponent.objects.get_or_create(company=c, code="HRA", defaults={"name":"HRA", "type":"earning", "account": acc("5100")})
    PayComponent.objects.get_or_create(company=c, code="PF", defaults={"name":"PF", "type":"deduction", "account": acc("2300")})
    self.stdout.write(self.style.SUCCESS("Payroll demo data ready"))
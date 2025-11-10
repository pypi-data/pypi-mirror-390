from django.template.loader import render_to_string
from weasyprint import HTML


def render_payslip_pdf(payslip, company) -> bytes:
    html = render_to_string("payroll/payslip.html", {"payslip": payslip, "company": company})
    pdf = HTML(string=html).write_pdf()
    return pdf
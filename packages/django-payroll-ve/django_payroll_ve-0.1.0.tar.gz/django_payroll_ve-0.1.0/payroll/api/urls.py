from django.urls import path
from payroll.api.views import EmployeeListCreate, PayComponentListCreate, PayslipCreatePost, PayslipPDF


urlpatterns = [
    path("employees/", EmployeeListCreate.as_view()),
    path("components/", PayComponentListCreate.as_view()),
    path("payslips/", PayslipCreatePost.as_view()),
    path("payslips/<int:pk>/pdf/", PayslipPDF.as_view()),
]
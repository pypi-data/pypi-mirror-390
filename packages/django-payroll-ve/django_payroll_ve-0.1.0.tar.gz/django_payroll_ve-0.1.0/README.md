# django-payroll-ve


## Install
```
pip install django-payroll-ve
```

## Settings
```
INSTALLED_APPS += ["rest_framework", "finacc", "payroll"]
PAYROLL = {"AUTO_POST": True}
```

## URLs
```
path("api/payroll/", include("payroll.api.urls"))
```

## Create & Post Payslip
```
POST /api/payroll/payslips/
{ "company": 1, "employee": 1, "period": "2025-11", "date": "2025-11-30", "currency": "INR",
"lines": [
{"component": 1, "amount": "50000.00"},
{"component": 2, "amount": "20000.00"},
{"component": 3, "amount": "1800.00"}
]
}
```


## Download PDF
```
GET /api/payroll/payslips/<id>/pdf/
```
from django.db import models

class Employee(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True)
    join_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("company", "code")

    def __str__(self):
        return f"{self.name} ({self.code})"

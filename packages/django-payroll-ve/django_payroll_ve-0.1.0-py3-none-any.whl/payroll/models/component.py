from django.db import models
class PayComponent(models.Model):
    TYPE_CHOICES = [
        ("earning", "Earning"),
        ("deduction", "Deduction"),
    ]
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT)

    class Meta:
        unique_together = ("company", "code")

    def __str__(self):
        return self.name

from django.db import models


class Payment(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    vendor = models.ForeignKey("purchase.Vendor", on_delete=models.PROTECT)
    date = models.DateField()
    currency = models.CharField(max_length=3, default="INR")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    via = models.CharField(max_length=16, choices=[("cash","cash"),("bank","bank")], default="bank")
    memo = models.CharField(max_length=255, blank=True)
    posted_entry_id = models.IntegerField(null=True, blank=True)


class SupplierRefund(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    vendor = models.ForeignKey("purchase.Vendor", on_delete=models.PROTECT)
    date = models.DateField()
    currency = models.CharField(max_length=3, default="INR")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    via = models.CharField(maxlength=16, choices=[("cash","cash"),("bank","bank")], default="bank")
    memo = models.CharField(max_length=255, blank=True)
    posted_entry_id = models.IntegerField(null=True, blank=True)
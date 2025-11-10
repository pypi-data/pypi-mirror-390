from decimal import Decimal
from django.db import models
from purchase.utils.money import q2


class VendorCredit(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    vendor = models.ForeignKey("purchase.Vendor", on_delete=models.PROTECT)
    number = models.CharField(max_length=32)
    date = models.DateField()
    currency = models.CharField(max_length=3, default="INR")
    bill = models.ForeignKey("purchase.PurchaseBill", on_delete=models.SET_NULL, null=True, blank=True)
    memo = models.CharField(max_length=255, blank=True)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    posted_entry_id = models.IntegerField(null=True, blank=True)


    class Meta:
        unique_together = ("company", "number")


def recompute(self):
    sub = Decimal("0"); tax = Decimal("0")
    for l in self.lines.all():
        sub += l.net_amount
        tax += l.tax_amount
    self.subtotal = q2(sub)
    self.tax_total = q2(tax)
    self.grand_total = q2(sub + tax)


class VendorCreditLine(models.Model):
    vendorcredit = models.ForeignKey(VendorCredit, on_delete=models.CASCADE, related_name="lines")
    item = models.ForeignKey("purchase.Item", on_delete=models.PROTECT)
    description = models.CharField(max_length=255, blank=True)
    qty = models.DecimalField(max_digits=18, decimal_places=4, default=1)
    rate = models.DecimalField(max_digits=18, decimal_places=2)
    discount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax = models.ForeignKey("finacc.Tax", on_delete=models.SET_NULL, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)


def recompute(self, is_inclusive=False):
    base = (self.rate * self.qty) - self.discount
    if not self.tax:
        self.net_amount = q2(base); self.tax_amount = q2(0); return
    tr = self.tax.rates.order_by("-effective_from").first()
    pct = (tr.percent if tr else 0) / 100
    if is_inclusive:
        net = base / (1 + pct); tax = base - net
    else:
        net = base; tax = base * pct
        self.net_amount = q2(net); self.tax_amount = q2(tax)
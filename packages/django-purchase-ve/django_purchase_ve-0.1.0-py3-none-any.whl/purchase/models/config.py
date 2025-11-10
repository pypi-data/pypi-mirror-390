from django.db import models


class AccountMapping(models.Model):
    company = models.OneToOneField("finacc.Company", on_delete=models.CASCADE)
    ap_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="purchase_ap")
    expense_product = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="purchase_exp_prod")
    expense_service = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="purchase_exp_serv")
    gst_receivable = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="purchase_gst_recv")
    # Optional ITC components to separate ledgers
    gst_cgst_input = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="purchase_cgst", null=True, blank=True)
    gst_sgst_input = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="purchase_sgst", null=True, blank=True)
    gst_igst_input = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="purchase_igst", null=True, blank=True)
    cash_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="purchase_cash")
    bank_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="purchase_bank")
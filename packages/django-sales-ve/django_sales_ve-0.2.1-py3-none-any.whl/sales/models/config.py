from django.db import models


class AccountMapping(models.Model):
    company = models.OneToOneField("finacc.Company", on_delete=models.CASCADE)
    ar_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="sales_ar")
    revenue_product = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="sales_rev_prod")
    revenue_service = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="sales_rev_serv")
    gst_payable = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="sales_gst_payable")
    # Optional: detailed GST components mapped to accounts (if you want per-component ledgers)
    gst_cgst = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="sales_cgst", null=True, blank=True)
    gst_sgst = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="sales_sgst", null=True, blank=True)
    gst_igst = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="sales_igst", null=True, blank=True)
    cash_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="sales_cash")
    bank_account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="sales_bank")
from django.db import models

class Quotation(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    opportunity = models.ForeignKey("crm.Opportunity", on_delete=models.SET_NULL, null=True, blank=True)
    contact = models.ForeignKey("crm.Contact", on_delete=models.PROTECT)
    number = models.CharField(max_length=32)
    date = models.DateField()
    currency = models.CharField(max_length=3, default="INR")
    is_tax_inclusive = models.BooleanField(default=False)
    memo = models.CharField(max_length=255, blank=True)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("company", "number")

class QuotationLine(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="lines")
    item = models.ForeignKey("sales.Item", on_delete=models.PROTECT)  # reuse products/services
    description = models.CharField(max_length=255, blank=True)
    qty = models.DecimalField(max_digits=18, decimal_places=4, default=1)
    rate = models.DecimalField(max_digits=18, decimal_places=2)
    discount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax = models.ForeignKey("finacc.Tax", on_delete=models.SET_NULL, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
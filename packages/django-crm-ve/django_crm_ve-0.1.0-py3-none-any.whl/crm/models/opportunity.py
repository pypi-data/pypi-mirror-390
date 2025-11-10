from django.db import models

class Stage(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    sequence = models.IntegerField(default=10)

    class Meta:
        unique_together = ("company", "name")
        ordering = ("sequence",)

class Opportunity(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    contact = models.ForeignKey("crm.Contact", on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    stage = models.ForeignKey(Stage, on_delete=models.PROTECT)
    expected_value = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="INR")
    close_date = models.DateField(null=True, blank=True)
    is_won = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
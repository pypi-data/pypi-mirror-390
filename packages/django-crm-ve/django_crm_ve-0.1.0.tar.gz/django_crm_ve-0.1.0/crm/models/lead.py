from django.db import models

class Lead(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=24, blank=True)
    source = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    converted_contact = models.ForeignKey("crm.Contact", on_delete=models.SET_NULL, null=True, blank=True)
    converted_opportunity = models.ForeignKey("crm.Opportunity", on_delete=models.SET_NULL, null=True, blank=True)
    is_converted = models.BooleanField(default=False)
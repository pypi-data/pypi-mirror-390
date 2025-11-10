from django.db import models

class Contact(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=24, blank=True)
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)
    is_customer = models.BooleanField(default=True)

    def __str__(self):
        return self.name
from django.db import models

class Activity(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    opportunity = models.ForeignKey("crm.Opportunity", on_delete=models.CASCADE, null=True, blank=True)
    contact = models.ForeignKey("crm.Contact", on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=16, choices=[("call","call"),("meeting","meeting"),("task","task")])
    subject = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    done = models.BooleanField(default=False)
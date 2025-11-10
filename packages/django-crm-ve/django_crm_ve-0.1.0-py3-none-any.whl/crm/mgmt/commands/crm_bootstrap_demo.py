from django.core.management.base import BaseCommand
from finacc.models.company import Company
from crm.models.contact import Contact
from crm.models.opportunity import Stage

class Command(BaseCommand):
    help = "Create CRM demo contacts and pipeline stages"

    def add_arguments(self, parser):
        parser.add_argument("--company", type=int, required=True)

    def handle(self, *args, **opts):
        c = Company.objects.get(id=opts["company"])
        Contact.objects.get_or_create(company=c, name="Demo Customer")
        names = ["New", "Qualified", "Proposal", "Won", "Lost"]
        for i, n in enumerate(names, start=1):
            Stage.objects.get_or_create(company=c, name=n, defaults={"sequence": i * 10})
        self.stdout.write(self.style.SUCCESS("CRM demo data ready"))
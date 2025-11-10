from decimal import Decimal
from sales.models.party import Customer
from sales.models.doc import SalesInvoice, SalesInvoiceLine
from sales.posting.adapters import post_sales_invoice
from sales.conf import get as sales_conf
from crm.models.contact import Contact
from crm.models.lead import Lead
from crm.models.opportunity import Opportunity, Stage
from crm.models.quotation import Quotation, QuotationLine


def convert_lead(company, lead: Lead):
    if lead.is_converted:
        return lead.converted_contact, lead.converted_opportunity
    contact = Contact.objects.create(company=company, name=lead.name, email=lead.email, phone=lead.phone)
    # Ensure Customer mirror in sales
    cust = Customer.objects.create(company=company, name=contact.name, email=contact.email, phone=contact.phone)
    stage = Stage.objects.filter(company=company).order_by("sequence").first()
    opp = Opportunity.objects.create(company=company, contact=contact, title=f"{contact.name} Opportunity", stage=stage, expected_value=0)
    lead.converted_contact = contact; lead.converted_opportunity = opp; lead.is_converted = True
    lead.save(update_fields=["converted_contact", "converted_opportunity", "is_converted"])
    return contact, opp


def recompute_quote(q: Quotation):
    from decimal import Decimal
    sub = Decimal("0"); tax = Decimal("0")
    for l in q.lines.select_related("tax").all():
        base = (l.rate * l.qty) - l.discount
        if not l.tax:
            l.net_amount = base; l.tax_amount = Decimal("0")
        else:
            tr = l.tax.rates.order_by("-effective_from").first()
            pct = (tr.percent if tr else 0) / 100
            if q.is_tax_inclusive:
                net = base / (1 + pct); t = base - net
            else:
                net = base; t = base * pct
            l.net_amount, l.tax_amount = net, t
        l.save(update_fields=["net_amount", "tax_amount"])
        sub += l.net_amount; tax += l.tax_amount
    q.subtotal = sub; q.tax_total = tax; q.grand_total = sub + tax
    q.save(update_fields=["subtotal", "tax_total", "grand_total"])


def confirm_quote_to_invoice(q: Quotation):
    """Create SalesInvoice from quote using django-sales and optionally auto-post."""
    recompute_quote(q)
    cust = Customer.objects.get(company=q.company, name=q.contact.name)  # simplistic sync
    inv = SalesInvoice.objects.create(company=q.company, customer=cust, number=f"INV-{q.number}", date=q.date, currency=q.currency, is_tax_inclusive=q.is_tax_inclusive, memo=q.memo)
    for l in q.lines.select_related("item", "tax").all():
        line = SalesInvoiceLine.objects.create(invoice=inv, item=l.item, description=l.description, qty=l.qty, rate=l.rate, discount=l.discount, tax=l.tax)
        line.recompute(inv.is_tax_inclusive); line.save(update_fields=["net_amount", "tax_amount"])
    inv.recompute(); inv.save(update_fields=["subtotal", "tax_total", "grand_total"])
    q.is_confirmed = True; q.save(update_fields=["is_confirmed"])
    if sales_conf("AUTO_POST_INVOICE"):
        post_sales_invoice(inv)
    return inv
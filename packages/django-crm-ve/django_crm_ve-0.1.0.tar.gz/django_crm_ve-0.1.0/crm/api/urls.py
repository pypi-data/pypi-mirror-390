from django.urls import path
from crm.api.views import ContactCreate, LeadCreateConvert, QuotationCreate, QuotationConfirmToInvoice

urlpatterns = [
    path("contacts/", ContactCreate.as_view()),
    path("leads/", LeadCreateConvert.as_view()),
    path("quotes/", QuotationCreate.as_view()),
    path("quotes/<int:pk>/confirm/", QuotationConfirmToInvoice.as_view()),
]
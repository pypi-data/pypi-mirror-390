from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from crm.api.serializers import (
    ContactSerializer, LeadSerializer, StageSerializer, OpportunitySerializer, ActivitySerializer,
    QuotationCreateSerializer,
)
from crm.models.lead import Lead
from crm.models.quotation import Quotation
from crm.services.converters import convert_lead, confirm_quote_to_invoice

class ContactCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = ContactSerializer(data=request.data); ser.is_valid(raise_exception=True); ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

class LeadCreateConvert(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = LeadSerializer(data=request.data); ser.is_valid(raise_exception=True)
        lead = ser.save()
        contact, opp = convert_lead(lead.company, lead)
        return Response({"lead_id": lead.id, "contact_id": contact.id, "opportunity_id": opp.id}, status=status.HTTP_201_CREATED)

class QuotationCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = QuotationCreateSerializer(data=request.data); ser.is_valid(raise_exception=True)
        q = ser.save();
        return Response({"quotation_id": q.id}, status=status.HTTP_201_CREATED)

class QuotationConfirmToInvoice(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        q = Quotation.objects.get(pk=pk)
        inv = confirm_quote_to_invoice(q)
        return Response({"quotation_id": q.id, "invoice_id": inv.id}, status=status.HTTP_201_CREATED)
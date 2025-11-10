from rest_framework import serializers
from crm.models.contact import Contact
from crm.models.lead import Lead
from crm.models.opportunity import Stage, Opportunity
from crm.models.activity import Activity
from crm.models.quotation import Quotation, QuotationLine

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = "__all__"

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"

class QuotationLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationLine
        fields = ["item", "description", "qty", "rate", "discount", "tax"]

class QuotationCreateSerializer(serializers.ModelSerializer):
    lines = QuotationLineSerializer(many=True)
    class Meta:
        model = Quotation
        fields = ["company", "opportunity", "contact", "number", "date", "currency", "is_tax_inclusive", "memo", "lines"]
    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        q = Quotation.objects.create(**validated_data)
        for l in lines:
            QuotationLine.objects.create(quotation=q, **l)
        return q
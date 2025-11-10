from django.conf import settings

DEFAULTS = {
    "DEFAULT_STAGE_PIPELINE": ["New", "Qualified", "Proposal", "Won", "Lost"],
    "DEFAULT_CURRENCY": "INR",
}
CRM = getattr(settings, "CRM", {})

def get(key: str):
    return CRM.get(key, DEFAULTS.get(key))
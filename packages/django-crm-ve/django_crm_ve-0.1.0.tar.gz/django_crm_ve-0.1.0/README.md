# django-crm-ve

## Install
```
pip install django-crm-ve
```
## Settings
```
INSTALLED_APPS += ["rest_framework", "finacc", "sales", "crm"]
```
## URLs
```
path("api/crm/", include("crm.api.urls"))
```
## Convert Lead → Contact + Opportunity
```
POST /api/crm/leads/
{ "company": 1, "name": "Foo Corp", "email": "foo@example.com" }
```
## Create Quote
```
POST /api/crm/quotes/
{ "company":1, "contact":1, "number":"Q-0001", "date":"2025-11-09", "currency":"INR",
  "lines": [{"item":1, "qty":"1.0", "rate":"1000.00", "tax":1}] }
```
## Confirm Quote → Sales Invoice (via django-sales)
```
POST /api/crm/quotes/<id>/confirm/
```
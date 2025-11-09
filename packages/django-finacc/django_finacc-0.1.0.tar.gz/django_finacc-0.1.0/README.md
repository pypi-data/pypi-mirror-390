# django-finacc


## Install
pip install django-finacc


## Settings
INSTALLED_APPS += ["rest_framework", "finacc"]


## URLs
path("api/finacc/", include("finacc.api.urls"))


## Migrate
python manage.py migrate


## Bootstrap CoA
python manage.py finacc_bootstrap_coa --company=1 --template=india_basic


## Post a Journal Entry (API)
POST /api/finacc/journal/entries/
{
"company": 1,
"date": "2025-11-08",
"currency": "INR",
"memo": "Opening capital",
"lines": [
{"account": 1, "debit": "100000.00", "credit": "0.00"},
{"account": 2, "debit": "0.00", "credit": "100000.00"}
]
}
## installation
INSTALLED_APPS += ["rest_framework", "finacc"]
FINACC = {
"BASE_CURRENCY": "INR",
"AUTO_POST_ON_CREATE": True,
}

## urls.py
from django.urls import include, path
urlpatterns = [
path("api/finacc/", include("finacc.api.urls")),
]


## Post programmatically

from finacc.posting.rules import create_simple_entry
from finacc.posting.engine import post_entry


je = create_simple_entry(company, date, "INR", "Sale", [
{"account": ar_acc, "debit": Decimal("1180.00")},
{"account": rev_acc, "credit": Decimal("1000.00")},
{"account": gst_payable_acc, "credit": Decimal("180.00")},
])
post_entry(je)


## Posting from sale and purchase
def post_invoice(company, invoice):
# map lines -> AR, Revenue, Tax
...
return post_entry(je)


## Implementation Notes & Roadmap

Immutable posted entries: disable updates/deletes; allow reversal entries only (planned: reverse_entry(entry_id)).

Reports: Add Ledger, Balance Sheet, P&L helpers with tree aggregation.

Tax: Load taxes_india_gst.json via setup script; provide posting helpers that split CGST/SGST/IGST to mapped accounts.

FX: Add revaluation utilities for period end.

Permissions: Add IsCompanyMember mixin to filter by company_id.

Docs site: mkdocs with Quickstart, API reference, diagrams.

CI: GitHub Actions matrix for Py3.11/3.12 and Django 5.0/5.1.


 
# django-sales


[![PyPI version](https://badge.fury.io/py/django-sales.svg)](https://pypi.org/project/django-sales/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-sales.svg)](https://pypi.org/project/django-sales/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


**Sales for Django** — products & services, invoices, credit notes, receipts, refunds, price lists, GST split, and automatic posting into [`django-finacc`](https://pypi.org/project/django-finacc/).


## Install
```bash
pip install django-sales
```

## Settings
```
INSTALLED_APPS += ["rest_framework", "finacc", "sales"]
SALES = {"AUTO_POST_INVOICE": True, "AUTO_POST_CREDITNOTE": True, "AUTO_POST_RECEIPT": True, "AUTO_POST_REFUND": True}
```
## URLs
```
path("api/sales/", include("sales.api.urls"))
```

### Create & Post an Invoice
```
POST /api/sales/invoices/
{ "company": 1, "customer": 1, "number": "S-0001", "date": "2025-11-09", "currency": "INR",
"is_tax_inclusive": false,
"lines": [{"item": 1, "qty": 1, "rate": "1000.00", "tax": 1}]
}
```

### Credit Note & Refund
```
POST /api/sales/credit-notes/ {...}
POST /api/sales/refunds/ {...}
```

### Mapping to Accounts

Create one sales.AccountMapping per company to point AR, Revenue, GST, Cash/Bank.

### GST Split

If finacc.TaxSplit exists for the selected tax, GST will be credited to CGST/SGST/IGST component accounts (if configured) or consolidated to gst_payable.

### License

MIT © 2025 Verified Enquiries

---


## 🚀 Publish to PyPI (build, twine, badges)


```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade build twine
python -m build
twine check dist/*
# TestPyPI
# twine upload --repository testpypi dist/*
# PyPI
# twine upload dist/*
```

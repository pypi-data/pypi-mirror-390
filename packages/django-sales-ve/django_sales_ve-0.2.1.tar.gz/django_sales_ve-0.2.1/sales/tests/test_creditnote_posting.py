import pytest
from decimal import Decimal
from sales.models.doc_creditnote import CreditNote, CreditNoteLine
from sales.models.item import Item, UoM
from sales.models.party import Customer
from sales.models.config import AccountMapping
from finacc.models.company import Company
from finacc.models.accounts import Account
from sales.posting.adapters import post_credit_note


@pytest.mark.django_db
def test_credit_note_posts():
    c = Company.objects.create(name="ACME")
    ar = Account.objects.create(company=c, code="1300", name="AR", kind="asset", normal_balance="debit")
    rev = Account.objects.create(company=c, code="4000", name="Sales", kind="income", normal_balance="credit")
    gst = Account.objects.create(company=c, code="2100", name="GST Payable", kind="liability", normal_balance="credit")
    cash = Account.objects.create(company=c, code="1000", name="Cash", kind="asset", normal_balance="debit")
    bank = Account.objects.create(company=c, code="1100", name="Bank", kind="asset", normal_balance="debit")
    AccountMapping.objects.create(company=c, ar_account=ar, revenue_product=rev, revenue_service=rev, gst_payable=gst, cash_account=cash, bank_account=bank)


    cust = Customer.objects.create(company=c, name="Foo")
    u = UoM.objects.create(code="pcs", name="Pieces")
    item = Item.objects.create(company=c, sku="PRD-001", name="Widget", type="product", uom=u, sales_price=1000)


    cn = CreditNote.objects.create(company=c, customer=cust, number="CN-1", date="2025-11-09", currency="INR")
    line = CreditNoteLine.objects.create(creditnote=cn, item=item, qty=1, rate=Decimal("1000.00"))
    line.recompute(False); line.save(); cn.recompute(); cn.save()


    entry = post_credit_note(cn)
    assert entry.is_posted and cn.posted_entry_id == entry.id
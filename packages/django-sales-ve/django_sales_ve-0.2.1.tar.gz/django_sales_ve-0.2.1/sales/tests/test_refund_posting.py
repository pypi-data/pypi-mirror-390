import pytest
from finacc.models.company import Company
from finacc.models.accounts import Account
from sales.models.party import Customer
from sales.models.doc_receipt import Refund
from sales.models.config import AccountMapping
from sales.posting.adapters import post_refund


@pytest.mark.django_db
def test_refund_posts():
    c = Company.objects.create(name="ACME")
    ar = Account.objects.create(company=c, code="1300", name="AR", kind="asset", normal_balance="debit")
    gst = Account.objects.create(company=c, code="2100", name="GST Payable", kind="liability", normal_balance="credit")
    rev = Account.objects.create(company=c, code="4000", name="Sales", kind="income", normal_balance="credit")
    cash = Account.objects.create(company=c, code="1000", name="Cash", kind="asset", normal_balance="debit")
    bank = Account.objects.create(company=c, code="1100", name="Bank", kind="asset", normal_balance="debit")
    AccountMapping.objects.create(company=c, ar_account=ar, revenue_product=rev, revenue_service=rev, gst_payable=gst, cash_account=cash, bank_account=bank)


    cust = Customer.objects.create(company=c, name="Foo")
    ref = Refund.objects.create(company=c, customer=cust, date="2025-11-09", currency="INR", amount="500.00", via="bank")
    entry = post_refund(ref)
    assert entry.is_posted and ref.posted_entry_id == entry.id
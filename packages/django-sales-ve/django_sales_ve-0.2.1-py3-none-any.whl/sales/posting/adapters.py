from decimal import Decimal
from finacc.posting.rules import create_simple_entry
from finacc.posting.engine import post_entry
from finacc.models.journal import JournalEntry
from sales.models.doc_invoice import SalesInvoice
from sales.models.doc_creditnote import CreditNote
from sales.models.doc_receipt import Receipt, Refund
from sales.models.config import AccountMapping
from sales.utils.tax import split_gst_amount




def _gst_lines(mapping, tax_amount, tax_model):
    """Return list of lines for GST split; falls back to gst_payable if component accounts missing."""
    splits = tax_model.splits.all() if tax_model else []
    portions = split_gst_amount(tax_amount, splits)
    lines = []
    # If component accounts configured, credit each; else credit consolidated gst_payable
    used_components = False
    if portions:
        for comp, amt in portions.items():
            if comp.upper() == "CGST" and mapping.gst_cgst:
                lines.append({"account": mapping.gst_cgst, "credit": amt, "debit": Decimal("0") , "description": comp})
                used_components = True
            elif comp.upper() == "SGST" and mapping.gst_sgst:
                lines.append({"account": mapping.gst_sgst, "credit": amt, "debit": Decimal("0"), "description": comp})
                used_components = True
            elif comp.upper() == "IGST" and mapping.gst_igst:
                lines.append({"account": mapping.gst_igst, "credit": amt, "debit": Decimal("0"), "description": comp})
                used_components = True
    if not used_components and tax_amount:
                lines.append({"account": mapping.gst_payable, "credit": tax_amount, "debit": Decimal("0"), "description": "GST"})
    return lines


def post_sales_invoice(invoice: SalesInvoice):
    mapping = AccountMapping.objects.get(company=invoice.company)
    lines = []
    # Revenue lines by item type
    main_tax_model = None
    for l in invoice.lines.select_related("item", "tax").all():
        rev_acc = mapping.revenue_service if l.item.type == "service" else mapping.revenue_product
        lines.append({"account": rev_acc, "credit": l.net_amount, "debit": Decimal("0"), "description": l.description or l.item.name})
        if l.tax:
            main_tax_model = l.tax
    # GST (split)
    lines.extend(_gst_lines(mapping, invoice.tax_total, main_tax_model))
    # AR
    lines.append({"account": mapping.ar_account, "debit": invoice.grand_total, "credit": Decimal("0"), "description": f"AR {invoice.number}"})


    je = create_simple_entry(invoice.company, invoice.date, invoice.currency, f"Invoice {invoice.number}", lines)
    posted = post_entry(je)
    invoice.posted_entry_id = posted.id; invoice.save(update_fields=["posted_entry_id"])
    return posted


def post_credit_note(cn: CreditNote):
    mapping = AccountMapping.objects.get(company=cn.company)
    lines = []
    main_tax_model = None
    # Reverse revenue (debit income), reduce GST payable (debit), reduce AR (credit)
    for l in cn.lines.select_related("item", "tax").all():
        rev_acc = mapping.revenue_service if l.item.type == "service" else mapping.revenue_product
        lines.append({"account": rev_acc, "debit": l.net_amount, "credit": Decimal("0"), "description": l.description or l.item.name})
        if l.tax:
            main_tax_model = l.tax
    # GST split as DEBIT (reducing payable)
    gst_lines = _gst_lines(mapping, cn.tax_total, main_tax_model)
    for gl in gst_lines:
        gl["debit"], gl["credit"] = gl.get("credit", Decimal("0")), Decimal("0")
    lines.extend(gst_lines)
    # Reduce AR
    lines.append({"account": mapping.ar_account, "credit": cn.grand_total, "debit": Decimal("0"), "description": f"CN {cn.number}"})


    je = create_simple_entry(cn.company, cn.date, cn.currency, f"Credit Note {cn.number}", lines)
    posted = post_entry(je)
    cn.posted_entry_id = posted.id; cn.save(update_fields=["posted_entry_id"])
    return posted


def post_receipt(rcpt: Receipt):
    mapping = AccountMapping.objects.get(company=rcpt.company)
    cash_or_bank = mapping.cash_account if rcpt.via == "cash" else mapping.bank_account
    lines = [
    {"account": cash_or_bank, "debit": rcpt.amount, "credit": Decimal("0"), "description": "Receipt"},
    {"account": mapping.ar_account, "credit": rcpt.amount, "debit": Decimal("0"), "description": "AR Settle"},
    ]
    je = create_simple_entry(rcpt.company, rcpt.date, rcpt.currency, "Receipt", lines)
    posted = post_entry(je)
    rcpt.posted_entry_id = posted.id; rcpt.save(update_fields=["posted_entry_id"])
    return posted

def post_refund(ref: Refund):
    mapping = AccountMapping.objects.get(company=ref.company)
    cash_or_bank = mapping.cash_account if ref.via == "cash" else mapping.bank_account
    lines = [
    {"account": cash_or_bank, "credit": ref.amount, "debit": Decimal("0"), "description": "Refund"},
    {"account": mapping.ar_account, "debit": ref.amount, "credit": Decimal("0"), "description": "AR Restore"},
    ]
    je = create_simple_entry(ref.company, ref.date, ref.currency, "Refund", lines)
    posted = post_entry(je)
    ref.posted_entry_id = posted.id; ref.save(update_fields=["posted_entry_id"])
    return posted
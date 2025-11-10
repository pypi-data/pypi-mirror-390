from decimal import Decimal
from finacc.posting.rules import create_simple_entry
from finacc.posting.engine import post_entry
from purchase.models.doc_bill import PurchaseBill
from purchase.models.doc_vendorcredit import VendorCredit
from purchase.models.doc_payment import Payment, SupplierRefund
from purchase.models.config import AccountMapping
from purchase.utils.tax import split_gst_amount




def _gst_itc_lines(mapping, tax_amount, tax_model):
    # Input tax credit (ITC) is debited to receivable accounts
    splits = tax_model.splits.all() if tax_model else []
    portions = split_gst_amount(tax_amount, splits)
    lines = []
    used_components = False
    if portions:
        for comp, amt in portions.items():
            if comp.upper() == "CGST" and mapping.gst_cgst_input:
                lines.append({"account": mapping.gst_cgst_input, "debit": amt, "credit": Decimal("0"), "description": comp})
                used_components = True
            elif comp.upper() == "SGST" and mapping.gst_sgst_input:
                lines.append({"account": mapping.gst_sgst_input, "debit": amt, "credit": Decimal("0"), "description": comp})
                used_components = True
            elif comp.upper() == "IGST" and mapping.gst_igst_input:
                lines.append({"account": mapping.gst_igst_input, "debit": amt, "credit": Decimal("0"), "description": comp})
                used_components = True
    if not used_components and tax_amount:
        lines.append({"account": mapping.gst_receivable, "debit": tax_amount, "credit": Decimal("0"), "description": "GST ITC"})
        return lines

def post_purchase_bill(bill: PurchaseBill):
    mapping = AccountMapping.objects.get(company=bill.company)
    lines = []
    main_tax_model = None
    # Expense lines by item type
    for l in bill.lines.select_related("item", "tax").all():
        exp_acc = mapping.expense_service if l.item.type == "service" else mapping.expense_product
        lines.append({"account": exp_acc, "debit": l.net_amount, "credit": Decimal("0"), "description": l.description or l.item.name})
        if l.tax:
            main_tax_model = l.tax
        # GST ITC debit lines
        lines.extend(_gst_itc_lines(mapping, bill.tax_total, main_tax_model))
        # AP credit line
        lines.append({"account": mapping.ap_account, "credit": bill.grand_total, "debit": Decimal("0"), "description": f"AP {bill.number}"})


    je = create_simple_entry(bill.company, bill.date, bill.currency, f"Bill {bill.number}", lines)
    posted = post_entry(je)
    bill.posted_entry_id = posted.id; bill.save(update_fields=["posted_entry_id"])
    return posted




def post_vendor_credit(vc: VendorCredit):
    mapping = AccountMapping.objects.get(company=vc.company)
    lines = []
    main_tax_model = None
    # Reverse expense (credit expense), reverse ITC (credit), reduce AP (debit)
    for l in vc.lines.select_related("item", "tax").all():
        exp_acc = mapping.expense_service if l.item.type == "service" else mapping.expense_product
        lines.append({"account": exp_acc, "credit": l.net_amount, "debit": Decimal("0"), "description": l.description or l.item.name})
        if l.tax:
            main_tax_model = l.tax
        # Credit ITC components / GST receivable
        itc_lines = _gst_itc_lines(mapping, vc.tax_total, main_tax_model)
        for il in itc_lines:
            il["credit"], il["debit"] = il.get("debit", Decimal("0")), Decimal("0")
        lines.extend(itc_lines)
    # AP debit
    lines.append({"account": mapping.ap_account, "debit": vc.grand_total, "credit": Decimal("0"), "description": f"VC {vc.number}"})


    je = create_simple_entry(vc.company, vc.date, vc.currency, f"Vendor Credit {vc.number}", lines)
    posted = post_entry(je)
    vc.posted_entry_id = posted.id; vc.save(update_fields=["posted_entry_id"])
    return posted




def post_payment(pmt: Payment):
    mapping = AccountMapping.objects.get(company=pmt.company)
    cash_or_bank = mapping.cash_account if pmt.via == "cash" else mapping.bank_account
    lines = [
    {"account": mapping.ap_account, "debit": pmt.amount, "credit": Decimal("0"), "description": "AP Settle"},
    {"account": cash_or_bank, "credit": pmt.amount, "debit": Decimal("0"), "description": "Payment"},
    ]
    je = create_simple_entry(pmt.company, pmt.date, pmt.currency, "Payment", lines)
    posted = post_entry(je)
    pmt.posted_entry_id = posted.id; pmt.save(update_fields=["posted_entry_id"])
    return posted




def post_supplier_refund(ref):
    mapping = AccountMapping.objects.get(company=ref.company)
    cash_or_bank = mapping.cash_account if ref.via == "cash" else mapping.bank_account
    lines = [
    {"account": cash_or_bank, "debit": ref.amount, "credit": Decimal("0"), "description": "Supplier Refund"},
    {"account": mapping.ap_account, "credit": ref.amount, "debit": Decimal("0"), "description": "AP Restore"},
    ]
    je = create_simple_entry(ref.company, ref.date, ref.currency, "Supplier Refund", lines)
    posted = post_entry(je)
    ref.posted_entry_id = posted.id; ref.save(update_fields=["posted_entry_id"])
    return posted
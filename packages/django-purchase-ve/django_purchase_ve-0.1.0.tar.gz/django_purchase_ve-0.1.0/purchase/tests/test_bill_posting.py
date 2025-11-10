import pytest
from decimal import Decimal
from finacc.models.company import Company
from finacc.models.accounts import Account
from purchase.models.party import Vendor
from purchase.models.item import UoM, Item
from purchase.models.doc_bill import PurchaseBill, PurchaseBillLine
from purchase.models.config import AccountMapping
from purchase.posting.adapters import post_purchase_bill


@pytest.mark.django_db
def test_bill_posts_to_finacc():
    c = Company.objects.create(name="ACME")
    ap = Account.objects.create(company=c, code="2000", name="AP", kind="liability", normal_balance="credit")
    gst_recv = Account.objects.create(company=c, code="2200", name="GST Receivable", kind="asset", normal_balance="debit")
    exp = Account.objects.create(company=c, code="5000", name="Expense", kind="expense", normal_balance="debit")
    cash = Account.objects.create(company=c, code="1000", name="Cash", kind="asset", normal_balance="debit")
    bank = Account.objects.create(company=c, code="1100", name="Bank", kind="asset", normal_balance="debit")
    AccountMapping.objects.create(company=c, ap_account=ap, expense_product=exp, expense_service=exp, gst_receivable=gst_recv, cash_account=cash, bank_account=bank)


    vend = Vendor.objects.create(company=c, name="Supplier")
    u = UoM.objects.create(code="pcs", name="Pieces")
    item = Item.objects.create(company=c, sku="PRD-001", name="Raw Mat", type="product", uom=u, purchase_price=300)


    bill = PurchaseBill.objects.create(company=c, vendor=vend, number="B-0001", date="2025-11-09", currency="INR")
    line = PurchaseBillLine.objects.create(bill=bill, item=item, qty=1, rate=Decimal("300.00"))
    line.recompute(False); line.save(); bill.recompute(); bill.save()


    entry = post_purchase_bill(bill)
    assert entry.is_posted and bill.posted_entry_id == entry.id
from django.core.management.base import BaseCommand
from finacc.models.company import Company
from finacc.models.accounts import Account
from purchase.models.party import Vendor
from purchase.models.item import UoM, Item
from purchase.models.config import AccountMapping


class Command(BaseCommand):
    help = "Create demo vendor, items and account mapping for Purchase"


def add_arguments(self, parser):
    parser.add_argument("--company", type=int, required=True)


def handle(self, *args, **opts):
    c = Company.objects.get(id=opts["company"])
    vend, _ = Vendor.objects.get_or_create(company=c, name="Default Vendor")
    u, _ = UoM.objects.get_or_create(code="pcs", defaults={"name":"Pieces"})
    Item.objects.get_or_create(company=c, sku="SVC-PUR-001", defaults={"name":"Freelance Service", "type":"service", "uom":u, "purchase_price":800})
    Item.objects.get_or_create(company=c, sku="PRD-PUR-001", defaults={"name":"Raw Material", "type":"product", "uom":u, "purchase_price":300})
    def acc(code): return Account.objects.get(company=c, code=code)
    AccountMapping.objects.get_or_create(company=c, defaults={
    "ap_account": acc("2000"),
    "expense_product": acc("5000"),
    "expense_service": acc("5000"),
    "gst_receivable": acc("2200"),
    "cash_account": acc("1000"),
    "bank_account": acc("1100"),
    })
    self.stdout.write(self.style.SUCCESS("Purchase demo data ready"))
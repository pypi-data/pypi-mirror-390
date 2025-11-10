from django.conf import settings


DEFAULTS = {
"AUTO_POST_BILL": True,
"AUTO_POST_VENDORCREDIT": True,
"AUTO_POST_PAYMENT": True,
"AUTO_POST_SUPPLIER_REFUND": True,
"DEFAULT_TAX_INCLUSIVE": False,
}
PURCHASE = getattr(settings, "PURCHASE", {})


def get(key: str):
    return PURCHASE.get(key, DEFAULTS.get(key))
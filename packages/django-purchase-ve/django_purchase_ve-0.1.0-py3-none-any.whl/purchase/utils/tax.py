from decimal import Decimal
from purchase.utils.money import q2


def split_gst_amount(tax_amount: Decimal, splits):
    tax_amount = Decimal(tax_amount or 0)
    if not splits:
        return {}
    total_share = sum([Decimal(s.share_percent) for s in splits]) or Decimal("100")
    remaining = tax_amount
    out = {}
    for i, comp in enumerate(splits):
        if i < len(splits) - 1:
            amt = q2(tax_amount * Decimal(comp.share_percent) / total_share)
            out[comp.component] = amt
            remaining -= amt
        else:
            out[comp.component] = q2(remaining)
    return out
from decimal import Decimal
from finacc.posting.rules import create_simple_entry
from finacc.posting.engine import post_entry
from fixedassets.models.asset import Asset
from fixedassets.models.movement import Acquisition, Revaluation, Impairment, Disposal
from fixedassets.models.schedule import DepreciationLine
from fixedassets.models.config import FAAccountMapping
from fixedassets.utils.money import q2


def post_acquisition(acq: Acquisition):
    a = acq.asset
    m = FAAccountMapping.objects.get(company=a.company)
    a.book_value = a.cost
    a.save(update_fields=["book_value"])
    lines = [
        {"account": m.asset_account, "debit": a.cost, "credit": Decimal("0"), "description": f"Acquire {a.code}"},
    ]
    je = create_simple_entry(a.company, acq.date, a.currency, f"FA Acquire {a.code}", lines)
    entry = post_entry(je)
    acq.posted_entry_id = entry.id; acq.save(update_fields=["posted_entry_id"])
    return entry


def post_depreciation(dline: DepreciationLine):
    a = dline.schedule.asset
    m = FAAccountMapping.objects.get(company=a.company)
    amt = q2(dline.amount)
    a.accumulated_depr = q2((a.accumulated_depr or 0) + amt)
    a.book_value = q2((a.book_value or a.cost) - amt)
    a.save(update_fields=["accumulated_depr", "book_value"])
    lines = [
        {"account": m.depr_expense_account, "debit": amt, "credit": Decimal("0"), "description": f"Depreciation {a.code}"},
        {"account": m.accum_depr_account, "credit": amt, "debit": Decimal("0"), "description": f"Accumulated {a.code}"},
    ]
    je = create_simple_entry(a.company, dline.date, a.currency, f"FA Depr {a.code}", lines)
    entry = post_entry(je)
    dline.posted_entry_id = entry.id; dline.is_posted = True
    dline.save(update_fields=["posted_entry_id", "is_posted"])
    return entry


def post_revaluation(rv: Revaluation):
    a = rv.asset
    m = FAAccountMapping.objects.get(company=a.company)
    delta = q2(rv.increase_amount - rv.decrease_amount)
    if delta == 0:
        return None
    a.book_value = q2((a.book_value or a.cost) + delta)
    a.save(update_fields=["book_value"])
    lines = []
    if delta > 0:
        # DR Asset, CR Revaluation Reserve (or Gain/Loss if reserve not set)
        lines.append({"account": m.asset_account, "debit": delta, "credit": Decimal("0")})
        credit_acc = m.revaluation_reserve or m.gain_loss_account
        lines.append({"account": credit_acc, "credit": delta, "debit": Decimal("0")})
    else:
        amt = abs(delta)
        # DR Loss/Reserve, CR Asset
        debit_acc = m.gain_loss_account
        lines.append({"account": debit_acc, "debit": amt, "credit": Decimal("0")})
        lines.append({"account": m.asset_account, "credit": amt, "debit": Decimal("0")})
    je = create_simple_entry(a.company, rv.date, a.currency, f"FA Reval {a.code}", lines)
    entry = post_entry(je)
    rv.posted_entry_id = entry.id; rv.save(update_fields=["posted_entry_id"])
    return entry


def post_impairment(im: Impairment):
    a = im.asset
    m = FAAccountMapping.objects.get(company=a.company)
    amt = q2(im.amount)
    a.book_value = q2((a.book_value or a.cost) - amt)
    a.save(update_fields=["book_value"])
    lines = [
        {"account": m.gain_loss_account, "debit": amt, "credit": Decimal("0")},
        {"account": m.asset_account, "credit": amt, "debit": Decimal("0")},
    ]
    je = create_simple_entry(a.company, im.date, a.currency, f"FA Impair {a.code}", lines)
    entry = post_entry(je)
    im.posted_entry_id = entry.id; im.save(update_fields=["posted_entry_id"])
    return entry


def post_disposal(ds: Disposal):
    a = ds.asset
    m = FAAccountMapping.objects.get(company=a.company)
    # Remove asset & accum, record gain/loss vs proceeds
    cost = a.cost
    accum = a.accumulated_depr or 0
    book = q2(cost - accum)
    proceeds = q2(ds.proceeds)
    diff = q2(proceeds - book)
    lines = [
        {"account": m.accum_depr_account, "debit": accum, "credit": Decimal("0")},     # clear accum
        {"account": m.asset_account, "credit": cost, "debit": Decimal("0")},           # clear asset
    ]
    if diff >= 0:
        # gain
        lines.append({"account": m.gain_loss_account, "credit": diff, "debit": Decimal("0")})
    else:
        lines.append({"account": m.gain_loss_account, "debit": abs(diff), "credit": Decimal("0")})
    # cash/bank not handled here; caller should post receipt separately or pass through bank account line
    je = create_simple_entry(a.company, ds.date, a.currency, f"FA Dispose {a.code}", lines)
    entry = post_entry(je)
    ds.posted_entry_id = entry.id; ds.save(update_fields=["posted_entry_id"])
    a.is_active = False; a.save(update_fields=["is_active"])
    return entry
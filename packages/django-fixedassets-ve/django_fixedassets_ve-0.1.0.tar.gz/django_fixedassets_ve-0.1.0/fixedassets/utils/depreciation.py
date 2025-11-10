from decimal import Decimal
from fixedassets.utils.money import q2

def slm_annual(cost: Decimal, residual: Decimal, life_years: int) -> Decimal:
    return q2((Decimal(cost) - Decimal(residual)) / Decimal(life_years))

def wdv_annual(opening: Decimal, rate_percent: Decimal) -> Decimal:
    return q2(Decimal(opening) * Decimal(rate_percent) / Decimal("100"))
from enum import Enum

class DepreciationMethod(str, Enum):
    SLM = "slm"  # straight-line
    WDV = "wdv"  # reducing balance (written down value)
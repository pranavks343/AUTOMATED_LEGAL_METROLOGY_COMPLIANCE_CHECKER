import re
from typing import Optional

def to_float_safe(x: Optional[str]) -> Optional[float]:
    if not x:
        return None
    try:
        # remove commas and non-digit/decimal chars except dot
        cleaned = re.sub(r'[^0-9\.]', '', x.replace(',', ''))
        return float(cleaned) if cleaned else None
    except Exception:
        return None

def find_first(patterns, text, flags=re.IGNORECASE):
    if not text:
        return None
    for pat in patterns:
        m = re.search(pat, text, flags)
        if m:
            return m.group(1) if m.groups() else m.group(0)
    return None

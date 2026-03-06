"""Salary data normalization utilities."""

import re


COMPANY_SIZE_MAP = {
    "스타트업": "startup",
    "startup": "startup",
    "중소": "mid",
    "mid": "mid",
    "중견": "mid",
    "대기업": "large",
    "large": "large",
    "enterprise": "large",
}

REGION_ALIASES = {
    "판교": "Pangyo",
    "서울": "Seoul",
    "부산": "Busan",
    "pangyo": "Pangyo",
    "seoul": "Seoul",
    "busan": "Busan",
}


def normalize_company_size(raw: str) -> str:
    """Normalize company size to: startup | mid | large."""
    key = raw.strip().lower()
    return COMPANY_SIZE_MAP.get(key, COMPANY_SIZE_MAP.get(raw.strip(), "mid"))


def normalize_region(raw: str) -> str:
    """Normalize region name to English canonical form."""
    key = raw.strip()
    return REGION_ALIASES.get(key, REGION_ALIASES.get(key.lower(), key))


def normalize_salary(value: int | str) -> int:
    """Normalize salary to integer KRW in 만원 units."""
    if isinstance(value, int):
        return value
    # strip commas, spaces
    cleaned = re.sub(r"[,\s]", "", str(value))
    return int(cleaned)

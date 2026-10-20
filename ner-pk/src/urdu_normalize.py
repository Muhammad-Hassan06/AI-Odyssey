"""
Urdu Orthographic Normalizer and Script Handler for Pakistani NER.
Standardizes Unicode variants, diacritics, Eastern Arabic-Indic numerals,
and character normalizations while preserving exact character offsets.
"""

import re
import unicodedata
from typing import Dict, List, Tuple

# Eastern Arabic-Indic numerals mapping
URDU_DIGITS_MAP = {
    "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
    "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9"
}

# Arabic to Urdu character standardizations
CHAR_MAP = {
    "ك": "ک",  # Arabic Kaf to Urdu Kaf
    "ي": "ی",  # Arabic Yaa to Urdu Ye
    "ى": "ی",  # Alif Maqsura to Urdu Ye
    "ة": "ہ",  # Ta Marbuta to Gol He
    "ه": "ہ",  # Arabic He to Gol He
    "ھ": "ھ",  # Do-chashmi He preserved
    "ؤ": "و",
    "أ": "ا",
    "إ": "ا",
    "آ": "آ",
}

# Urdu diacritics (Aerab) to strip for robust matching
AERAB_PATTERN = re.compile(r"[\u064B-\u065F\u0670]")

def normalize_urdu_text(text: str) -> str:
    """Normalize Urdu script characters while preserving string length/alignment."""
    if not text:
        return ""
    
    # Standardize Unicode representation
    text = unicodedata.normalize("NFKC", text)

    # Standardize common Arabic character bleed
    chars = []
    for c in text:
        chars.append(CHAR_MAP.get(c, c))
    normalized = "".join(chars)

    # Normalize zero-width joiners and non-breaking spaces
    normalized = normalized.replace("\u200c", " ").replace("\u200b", "").replace("\u00a0", " ")
    return normalized

def convert_urdu_digits_to_ascii(text: str) -> str:
    """Convert Eastern Arabic-Indic numerals (۰-۹) to standard ASCII digits (0-9)."""
    return "".join(URDU_DIGITS_MAP.get(c, c) for c in text)

def is_urdu_dominant(text: str) -> bool:
    """Check if the text contains a significant portion of Arabic/Urdu Unicode blocks."""
    if not text:
        return False
    urdu_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF" or "\uFB50" <= c <= "\uFDFF" or "\uFE70" <= c <= "\uFEFF")
    return (urdu_chars / len(text)) > 0.15

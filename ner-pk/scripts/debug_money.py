import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import re
from src.rules import MONEY_REGEXES, heal_ocr_numeric_noise

text = 'Federal Budget 2025-26 mein FBR ne Rs 14.1 trillion ka target rakha, PKR 450,000 ki tankhwah par 12.5 per cent tax, aur 50 ارب ڈالر ka qarza 1 July 2025 se ۳۰ جون ۲۰۲۶ tak chukana hai.'
healed = heal_ocr_numeric_noise(text)
print('Healed text diff:', text != healed)

for idx, r in enumerate(MONEY_REGEXES):
    for m in r.finditer(text):
        print(f'Text Match Regex {idx}: "{m.group(0)}" at {m.span()}')
    for m in r.finditer(healed):
        print(f'Healed Match Regex {idx}: "{m.group(0)}" at {m.span()}')

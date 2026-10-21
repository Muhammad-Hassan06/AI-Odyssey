import os

path = os.path.join(os.path.dirname(__file__), "..", "src", "preannotate.py")
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add Bank Names to ORGANIZATIONS
bank_names = [
    "Sindh Bank", "Bank Alfalah Limited", "Bank Alfalah", "Meezan Bank",
    "Faysal Bank", "Askari Bank", "Soneri Bank", "JS Bank", "Al Baraka Bank",
    "Dubai Islamic Bank", "Standard Chartered Bank", "Habib Metropolitan Bank",
    "Bank of Khyber", "Zarai Taraqiati Bank", "ZTBL"
]

for b in bank_names:
    if f'"{b}"' not in code:
        code = code.replace(
            '"Jazz", "Ufone", "Telenor", "Zong"',
            f'"Jazz", "Ufone", "Telenor", "Zong",\n    "{b}"'
        )

# 2. Add Urdu Prominent Persons to PROMINENT_PERSONS
urdu_persons = [
    "شاہین آفریدی", "شاہین شاہ آفریدی", "محمد رضوان", "نسیم شاہ", "فخر زمان",
    "شاداب خان", "حارث رؤف", "محمد عامر", "یحییٰ خان", "ایوب خان",
    "لیاقت علی خان", "ذوالفقار علی بھٹو", "مریم نواز", "آصف علی زرداری"
]

for p in urdu_persons:
    if f'"{p}"' not in code:
        code = code.replace(
            '"عائشہ خان"',
            f'"عائشہ خان", "{p}"'
        )

# 3. Add Pakistani Name Pattern (Muhammad Bilal, Syed Ali, etc.)
name_pat_code = '''
    # 1.6 Common Pakistani Personal Name convention (Muhammad Bilal, Syed Ali, Hafiz Naeem etc.)
    PAK_NAME_PATTERN = re.compile(
        r"\\b(?:Muhammad|Mohammad|Mohd\\.?|Syed|Hafiz|Malik)\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)?)\\b"
    )
    for m in PAK_NAME_PATTERN.finditer(text):
        full_name = m.group(0).strip()
        candidates.append({
            "text": full_name,
            "start": m.start(),
            "end": m.end(),
            "label": "PERSON",
            "priority": 9
        })
'''

if 'PAK_NAME_PATTERN =' not in code:
    code = code.replace(
        '# 2. Gazetteer entities with OCR/typo word healing',
        name_pat_code + '\n    # 2. Gazetteer entities with OCR/typo word healing'
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Applied Claude fixes to src/preannotate.py successfully!")

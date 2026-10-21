import os
import re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
preannotate_path = os.path.join(base_dir, 'src', 'preannotate.py')
postprocess_path = os.path.join(base_dir, 'src', 'postprocess.py')

# 1. Update src/preannotate.py
with open(preannotate_path, 'r', encoding='utf-8') as f:
    pre_code = f.read()

# Add Jazz, Ufone, Telenor, Zong to ORGANIZATIONS if not present
if '"Jazz"' not in pre_code:
    pre_code = pre_code.replace(
        '"World Bank", "Asian Development Bank", "ADB", "State Bank", "Federal Board of Revenue"',
        '"World Bank", "Asian Development Bank", "ADB", "State Bank", "Federal Board of Revenue",\n    "Jazz", "Ufone", "Telenor", "Zong"'
    )

# Common sensitive set definition
sensitive_def = '''COMMON_SENSITIVE = {
    "Dawn", "The Nation", "Nation", "Jazz", "Express", "United", "Sun", "Star",
    "NAB", "FIA", "ECP", "FBR", "PIA", "PBS", "PEMRA", "LUMS", "NUST", "NADRA",
    "MQM", "PTI", "PML", "PPP", "ANP", "JUI", "OGDCL", "PSO", "SNGPL", "SSGC",
    "NBP", "HBL", "UBL", "MCB", "BOP", "IMF", "ADB", "PECA", "CrPC", "PPC", "SC", "SCP",
    "LHC", "SHC", "PHC", "IHC", "BHC", "FSC", "JCP", "SJC", "ATC", "PCB", "KCCI", "LCCI", "SCBA"
}
'''

if 'COMMON_SENSITIVE =' not in pre_code:
    pre_code = sensitive_def + '\n' + pre_code

# Replace load_gazetteers loop for boundaries and case sensitivity
old_load_gaz = '''        for term in terms:
            term_clean = term.strip()
            if not term_clean:
                continue
            # Handle English vs Urdu boundary
            if any(ord(c) > 127 for c in term_clean):
                pat = re.compile(re.escape(term_clean))
            else:
                pat = re.compile(rf"\\b{re.escape(term_clean)}\\b", re.IGNORECASE)

            # Assign priority based on specificity
            priority = 8 if label in ["COURT_LEGAL_BODY", "LAW_ACT", "SPORTS_TEAM", "EDUCATIONAL_INSTITUTION", "POLITICAL_PARTY"] else 6
            compiled_patterns.append((pat, label, priority))'''

new_load_gaz = '''        for term in terms:
            term_clean = term.strip()
            if not term_clean:
                continue
            # Handle English vs Urdu boundary
            if any(ord(c) > 127 for c in term_clean):
                pat = re.compile(rf"(?<![\\u0600-\\u06FF]){re.escape(term_clean)}(?![\\u0600-\\u06FF])")
            else:
                if term_clean in COMMON_SENSITIVE or (len(term_clean) <= 5 and term_clean.isupper()):
                    pat = re.compile(rf"\\b{re.escape(term_clean)}\\b")
                else:
                    pat = re.compile(rf"\\b{re.escape(term_clean)}\\b", re.IGNORECASE)

            # Assign priority based on specificity
            priority = 8 if label in ["COURT_LEGAL_BODY", "LAW_ACT", "SPORTS_TEAM", "EDUCATIONAL_INSTITUTION", "POLITICAL_PARTY"] else 6
            compiled_patterns.append((pat, label, priority))'''

pre_code = pre_code.replace(old_load_gaz, new_load_gaz)

# Also update Countries and Orgs in load_gazetteers
old_orgs_compile = '''    for org in sorted(ORGANIZATIONS, key=lambda o: len(o), reverse=True):
        pat = re.compile(rf"\\b{re.escape(org)}\\b", re.IGNORECASE)
        compiled_patterns.append((pat, "ORGANIZATION", 7))'''

new_orgs_compile = '''    for org in sorted(ORGANIZATIONS, key=lambda o: len(o), reverse=True):
        if org in COMMON_SENSITIVE or (len(org) <= 5 and org.isupper()):
            pat = re.compile(rf"\\b{re.escape(org)}\\b")
        else:
            pat = re.compile(rf"\\b{re.escape(org)}\\b", re.IGNORECASE)
        compiled_patterns.append((pat, "ORGANIZATION", 7))'''

pre_code = pre_code.replace(old_orgs_compile, new_orgs_compile)

# Update English and Urdu honorific extractors in preannotate_sentence
old_honorific_en = '''    HONORIFIC_EN_PATTERN = re.compile(
        r"\\b(?:Justice|Chief Justice|Judge|Dr\\.?|Doctor|Prof\\.?|Professor|Mr\\.?|Ms\\.?|Mrs\\.?|Barrister|Advocate|Senator|Gen\\.?|General|Maj\\.?|Major|Capt\\.?|Captain|Col\\.?|Colonel|Maulana|Mufti|Chaudhry|Chaudhary|Sardar|Pir|Makhdoom)\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+){1,3})\\b"
    )
    for m in HONORIFIC_EN_PATTERN.finditer(text):
        name_text = m.group(1)
        candidates.append({
            "text": name_text,
            "start": m.start(1),
            "end": m.end(1),
            "label": "PERSON",
            "priority": 10 # High priority: beats accidental CITY or PROVINCE matches on parts of name (e.g. Dr. Multan Khan -> Multan Khan)
        })'''

new_honorific_en = '''    PREFIX_TITLES_EN = (
        r'(?:Chief\\s+Justice|Justice|Judge|'
        r'Lt\\.?\\s*Gen\\.?|Lieutenant\\s+General|Gen\\.?|General|Maj\\.?\\s*Gen\\.?|Major\\s+General|Brig\\.?|Brigadier|Col\\.?|Colonel|Maj\\.?|Major|Capt\\.?|Captain|'
        r'Prof\\.?\\s*Dr\\.?|Prof\\.?|Professor|Dr\\.?|Doctor|'
        r'Barrister|Advocate|Senator|'
        r'Chairman|Chairperson|President|Prime\\s+Minister|Chief\\s+Minister|Minister|Governor|Director\\s+General|DG|Director|CEO|Inspector\\s+General|IG|'
        r'Anchor|'
        r'Mohtarma|Sahibzada|Makhdoom|Pir|Sardar|Chaudhry|Chaudhary|Mr\\.?|Ms\\.?|Mrs\\.?|Maulana|Mufti)'
        r'(?:\\s*\\((?:Retd\\.?|retd\\.?|R)\\))?'
    )
    HONORIFIC_EN_PATTERN = re.compile(
        rf'\\b{PREFIX_TITLES_EN}\\s+([A-Z][a-zA-Z\\-]*(?:\\s+[A-Z][a-zA-Z\\-]*){{0,3}})\\b'
    )
    for m in HONORIFIC_EN_PATTERN.finditer(text):
        raw_name = m.group(1).strip()
        name_text = re.sub(r"\\s+(?:Sahib|Sahiba)$", "", raw_name).strip()
        end_pos = m.start(1) + len(name_text)
        candidates.append({
            "text": name_text,
            "start": m.start(1),
            "end": end_pos,
            "label": "PERSON",
            "priority": 12
        })'''

pre_code = pre_code.replace(old_honorific_en, new_honorific_en)

old_honorific_ur = '''    HONORIFIC_UR_PATTERN = re.compile(
        r"(?:جسٹس|چیف جسٹس|ڈاکٹر|پروفیسر|علامہ|مولانا|مفتی|سینیٹر|بیرسٹر|ایڈووکیٹ|سردار|چوہدری|مخدوم|پیر)\\s+([\\u0600-\\u06FF]+(?:\\s+[\\u0600-\\u06FF]+){1,3})"
    )
    for m in HONORIFIC_UR_PATTERN.finditer(text):
        name_text = m.group(1).strip()
        candidates.append({
            "text": name_text,
            "start": m.start(1),
            "end": m.end(1),
            "label": "PERSON",
            "priority": 10
        })'''

new_honorific_ur = '''    URDU_PREFIXES = (
        r'(?:جسٹس\\s*(?:\\([رR]\\))?|چیف\\s*جسٹس\\s*(?:\\([رR]\\))?|'
        r'ڈاکٹر|پروفیسر|علامہ|مولانا|مفتی|سینیٹر|بیرسٹر|ایڈووکیٹ|'
        r'سردار|مخدوم|پیر|صاحبزادہ|محترمہ|'
        r'ملزم|مجرم|مقتول|مدعی|مفرور)'
    )
    URDU_HONORIFIC_PAT = re.compile(
        rf'(?<![\\u0600-\\u06FF]){URDU_PREFIXES}\\s+([\\u0600-\\u06FF]+(?:\\s+[\\u0600-\\u06FF]+){{0,3}})'
    )
    URDU_POSTPOSITIONS = {'کا', 'کی', 'کے', 'نے', 'کو', 'سے', 'میں', 'پر', 'تک', 'اور', 'یا'}
    for m in URDU_HONORIFIC_PAT.finditer(text):
        raw_name = m.group(1).strip()
        raw_name = re.sub(r'\\s+(?:صاحب|صاحبہ)$', '', raw_name).strip()
        tokens = raw_name.split()
        valid_tokens = []
        for t in tokens:
            if t in URDU_POSTPOSITIONS or any(c.isdigit() or ('۰' <= c <= '۹') for c in t):
                break
            valid_tokens.append(t)
        if valid_tokens:
            final_name = ' '.join(valid_tokens)
            end_pos = m.start(1) + len(final_name)
            candidates.append({
                "text": final_name,
                "start": m.start(1),
                "end": end_pos,
                "label": "PERSON",
                "priority": 12
            })'''

pre_code = pre_code.replace(old_honorific_ur, new_honorific_ur)

with open(preannotate_path, 'w', encoding='utf-8') as f:
    f.write(pre_code)

print("Updated preannotate.py successfully!")

# 2. Update src/postprocess.py
with open(postprocess_path, 'r', encoding='utf-8') as f:
    post_code = f.read()

# Add false positive prune guard function
prune_func = '''
FALSE_POSITIVE_WORDS = {
    "MEDIA_OUTLET": {"dawn", "nation", "the nation", "star", "sun", "today", "express", "رات"},
    "GOVERNMENT_BODY": {"nab"},
    "ORGANIZATION": {"jazz", "united", "express"}
}

def is_unwanted_false_positive(text: str, ent: Dict[str, Any]) -> bool:
    lbl = ent["label"]
    start, end = ent["start"], ent["end"]
    span = text[start:end].strip()
    span_lower = span.lower()

    if lbl in FALSE_POSITIVE_WORDS:
        if span_lower in FALSE_POSITIVE_WORDS[lbl]:
            # Proper nouns must be Title Case or UPPERCASE, not lowercase homonyms
            if span.islower() or span == "رات":
                return True
            if span_lower == "the nation":
                # Guard against "the nation's economy" or "addressed the nation"
                surrounding = text[max(0, start - 15):min(len(text), end + 15)].lower()
                if "'s" in text[end:end+2] or any(w in surrounding for w in ["addressed", "across", "for", "economy", "centre of"]):
                    return True
    return False
'''

if 'FALSE_POSITIVE_WORDS =' not in post_code:
    # insert before clean_span_boundaries
    post_code = post_code.replace('def clean_span_boundaries(', prune_func + '\ndef clean_span_boundaries(')

# In clean_span_boundaries, filter out unwanted false positives
old_append = '''        cleaned.append({
            "text": text[start:end],
            "start": start,
            "end": end,
            "label": label
        })'''

new_append = '''        cand_ent = {
            "text": text[start:end],
            "start": start,
            "end": end,
            "label": label
        }
        if not is_unwanted_false_positive(text, cand_ent):
            cleaned.append(cand_ent)'''

post_code = post_code.replace(old_append, new_append)

# In hybrid_merge_predictions, elevate rule PERSON priority to 85
old_rule_prio = '''        if lbl in DETERMINISTIC_RULE_LABELS:
            priority = 100
        elif lbl in GAZETTEER_LABELS:
            priority = 80
        else:
            priority = 60'''

new_rule_prio = '''        if lbl in DETERMINISTIC_RULE_LABELS:
            priority = 100
        elif lbl in GAZETTEER_LABELS or lbl == "PERSON":
            priority = 85
        else:
            priority = 60'''

post_code = post_code.replace(old_rule_prio, new_rule_prio)

with open(postprocess_path, 'w', encoding='utf-8') as f:
    f.write(post_code)

print("Updated postprocess.py successfully!")

with open('src/postprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add LANDMARK_FACILITY to GAZETTEER_LABELS
old_gaz = '''    GAZETTEER_LABELS = {
        "COURT_LEGAL_BODY", "GOVERNMENT_BODY", "LAW_ACT", "POLITICAL_PARTY",
        "EDUCATIONAL_INSTITUTION", "MEDIA_OUTLET", "SPORTS_TEAM", "CITY",
        "PROVINCE_REGION", "COUNTRY", "ORGANIZATION", "EVENT"
    }'''

new_gaz = '''    GAZETTEER_LABELS = {
        "COURT_LEGAL_BODY", "GOVERNMENT_BODY", "LAW_ACT", "POLITICAL_PARTY",
        "EDUCATIONAL_INSTITUTION", "MEDIA_OUTLET", "SPORTS_TEAM", "CITY",
        "PROVINCE_REGION", "COUNTRY", "ORGANIZATION", "EVENT", "LANDMARK_FACILITY"
    }'''

assert old_gaz in content, "old_gaz not found"
content = content.replace(old_gaz, new_gaz, 1)

# 2. Preserve opening parenthesis for phone numbers
old_strip = '''        # 2. Strip leading whitespace or punctuation
        while start < end and (text[start] in PUNCTUATION_TO_STRIP or text[start].isspace()):
            start += 1'''

new_strip = '''        # 2. Strip leading whitespace or punctuation
        while start < end and (text[start] in PUNCTUATION_TO_STRIP or text[start].isspace()):
            if label == "PHONE_NUMBER" and text[start] == "(" and ")" in text[start:end]:
                break
            start += 1'''

assert old_strip in content, "old_strip not found"
content = content.replace(old_strip, new_strip, 1)

with open('src/postprocess.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: Updated postprocess.py with LANDMARK_FACILITY and PHONE_NUMBER fixes")

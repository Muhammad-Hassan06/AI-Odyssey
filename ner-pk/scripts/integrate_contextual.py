with open('src/preannotate.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import
old_import = "from src.rules import extract_regex_entities"
new_import = "from src.rules import extract_regex_entities\nfrom src.contextual_grammar import extract_contextual_entities"
assert old_import in content, "old_import not found"
content = content.replace(old_import, new_import, 1)

# 2. Call extract_contextual_entities in preannotate_sentence
old_regex_block = """    # 1. Regex rule entities (PHONE, ID, MONEY, PERCENT, TIME, DATE)
    regex_ents = extract_regex_entities(text)
    for ent in regex_ents:
        candidates.append({
            "text": ent["text"],
            "start": ent["start"],
            "end": ent["end"],
            "label": ent["label"],
            "priority": 10
        })"""

new_regex_block = """    # 1. Regex rule entities (PHONE, ID, MONEY, PERCENT, TIME, DATE)
    regex_ents = extract_regex_entities(text)
    for ent in regex_ents:
        candidates.append({
            "text": ent["text"],
            "start": ent["start"],
            "end": ent["end"],
            "label": ent["label"],
            "priority": 10
        })

    # 1.2 Contextual Syntactic Grammar entities (Sports match vs Country, legal filings, accused, etc.)
    context_ents = extract_contextual_entities(text)
    candidates.extend(context_ents)"""

assert old_regex_block in content, "old_regex_block not found"
content = content.replace(old_regex_block, new_regex_block, 1)

with open('src/preannotate.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: integrated contextual grammar into preannotate.py")

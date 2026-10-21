with open('src/preannotate.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = """        candidates.append({
            "text": team2,
            "start": m.start(2),
            "end": m.start(2) + len(team2),
            "label": "SPORTS_TEAM",
            "priority": 11
        })"""

repl = """        candidates.append({
            "text": team2,
            "start": m.start(2),
            "end": m.start(2) + len(team2),
            "label": "SPORTS_TEAM",
            "priority": 11
        })

    # 1.8 Sports player signing / transaction pattern
    SIGN_PAT = re.compile(r"\\b(?:Sign|Signs|Signed|Draft|Drafts|Drafted|Appoint|Appoints|Pick|Picks)\\s+([A-Z][a-z]+)\\b")
    for m in SIGN_PAT.finditer(text):
        player = m.group(1).strip()
        candidates.append({
            "text": player,
            "start": m.start(1),
            "end": m.end(1),
            "label": "PERSON",
            "priority": 9
        })"""

assert target in content, "target not found"
content = content.replace(target, repl, 1)

with open('src/preannotate.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: Added SIGN_PAT to preannotate.py")

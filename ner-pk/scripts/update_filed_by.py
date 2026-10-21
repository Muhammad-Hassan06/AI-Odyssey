with open('src/contextual_grammar.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_pat = """    # 2.2 Legal filing: "...petition / appeal filed by [Name]" / "...moved by [Name]"
    FILED_BY_PAT = re.compile(
        rf"\\b(?:petition|appeal|plea|complaint|case)\\s+(?:filed|moved|lodged|submitted)\\s+by\\s+({CAP_NAME})\\b",
        re.IGNORECASE
    )"""

new_pat = """    # 2.2 Legal filing: "...petition was filed by [Name]" / "filed by [Name]"
    FILED_BY_PAT = re.compile(
        rf"(?:\\b(?:petition|appeal|plea|complaint|case)\\s+(?:was\\s+|is\\s+|has\\s+been\\s+)?|\\b)(?:filed|moved|lodged|submitted|argued|represented)\\s+by\\s+({CAP_NAME})\\b",
        re.IGNORECASE
    )"""

assert old_pat in content, "old_pat not found"
content = content.replace(old_pat, new_pat, 1)

with open('src/contextual_grammar.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: Updated FILED_BY_PAT in contextual_grammar.py")

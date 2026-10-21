with open('src/postprocess.py', 'r', encoding='utf-8') as f:
    content = f.read()

target1 = """            # Keep % for PERCENT
            if label == "PERCENT" and text[end - 1] == "%":
                break"""

repl1 = """            # Keep % for PERCENT
            if label == "PERCENT" and text[end - 1] == "%":
                break
            # Keep dot for a.m. and p.m. in TIME
            if label == "TIME" and text[start:end].lower().endswith(("a.m.", "p.m.")):
                break"""

target2 = """    if confidence_thresholds is None:
        confidence_thresholds = {
            "PERSON": 0.60,
            "LANDMARK_FACILITY": 0.55,
            "ORGANIZATION": 0.50,
            "GOVERNMENT_BODY": 0.50,
            "DATE": 0.50
        }"""

repl2 = """    if confidence_thresholds is None:
        confidence_thresholds = {
            "PERSON": 0.40,
            "LANDMARK_FACILITY": 0.40,
            "ORGANIZATION": 0.40,
            "GOVERNMENT_BODY": 0.40,
            "DATE": 0.35
        }"""

assert target1 in content, "target1 not found"
assert target2 in content, "target2 not found"

content = content.replace(target1, repl1, 1).replace(target2, repl2, 1)
with open('src/postprocess.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: Updated postprocess.py")

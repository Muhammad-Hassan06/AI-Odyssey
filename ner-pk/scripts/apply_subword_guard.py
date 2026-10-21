import os

path = os.path.join(os.path.dirname(__file__), "..", "src", "postprocess.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_is_unwanted = """def is_unwanted_false_positive(text: str, ent: Dict[str, Any]) -> bool:
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
    return False"""

new_is_unwanted = """def is_unwanted_false_positive(text: str, ent: Dict[str, Any]) -> bool:
    lbl = ent["label"]
    start, end = ent["start"], ent["end"]
    span = text[start:end].strip()
    span_lower = span.lower()

    # 1. Single-letter alphabetic fragment (e.g. "n", "s") is an orphan subword, never an entity!
    if len(span) <= 1 and span.isalpha():
        return True

    # 2. Subword fragment that cuts inside an alphanumeric word boundary
    if start > 0 and text[start - 1].isalnum() and text[start].isalnum():
        return True
    if end < len(text) and text[end - 1].isalnum() and text[end].isalnum():
        return True

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
    return False"""

content = content.replace(old_is_unwanted, new_is_unwanted)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated is_unwanted_false_positive successfully!")

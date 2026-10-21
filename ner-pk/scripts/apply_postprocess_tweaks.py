import os

path = os.path.join(os.path.dirname(__file__), "..", "src", "postprocess.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update false positive words to include "daw"
content = content.replace(
    '"MEDIA_OUTLET": {"dawn", "nation", "the nation", "star", "sun", "today", "express", "رات"}',
    '"MEDIA_OUTLET": {"dawn", "daw", "nation", "the nation", "star", "sun", "today", "express", "رات"}'
)

# 2. Prevent merging statute with section
old_merge = """        # Check if same label and separated only by a space or hyphen
        gap = text[prev["end"]:current["start"]]
        if prev["label"] == current["label"] and gap in [" ", "-", ""]:
            # Merge into prev"""

new_merge = """        # Check if same label and separated only by a space or hyphen
        gap = text[prev["end"]:current["start"]]
        if prev["label"] == current["label"] and gap in [" ", "-", ""]:
            # Do not merge statute name (e.g. CrPC, PPC) with statutory section (e.g. Section 144)
            if prev["label"] == "LAW_ACT" and current["text"].startswith(("Section", "Sec.", "Article", "Art.", "دفعہ", "آرٹیکل")):
                merged.append(current)
                continue
            # Merge into prev"""

content = content.replace(old_merge, new_merge)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("postprocess.py updated successfully!")

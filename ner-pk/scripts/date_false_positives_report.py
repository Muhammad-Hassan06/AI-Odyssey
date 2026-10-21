import json
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from src.rules import extract_regex_entities

# Old patterns for comparison
OLD_MONTHS = r"January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
OLD_DAYS = r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun"
OLD_DATE_REGEXES = [
    re.compile(rf"(?i)\b\d{{1,2}}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:{OLD_MONTHS})(?:[,\s]+\d{{4}})?\b"),
    re.compile(rf"(?i)\b(?:{OLD_MONTHS})\s+\d{{1,2}}(?:st|nd|rd|th)?(?:[,\s]+\d{{4}})?\b"),
    re.compile(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b"),
    re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b"),
    re.compile(rf"(?i)\b(?:{OLD_DAYS})\b"),
    re.compile(r"(?:[0-9۰-۹]{1,2}|یکم)\s*(?:جنوری|فروری|مارچ|اپریل|مئی|جون|جولائی|اگست|ستمبر|اکتوبر|نومبر|دسمبر)(?:\s*[0-9۰-۹]{4})?"),
    re.compile(r"\b(?:پیر|منگل|بدھ|جمعرات|جمعہ|ہفتہ|اتوار)\b"),
    re.compile(r"(?:[0-9۰-۹]{1,2}|یکم)\s*(?:محرم(?:\s*الحرام)?|صفر|ربیع\s*(?:الاول|الثانی)|جمادی\s*(?:الاول|الثانی)|رجب|شعبان|رمضان(?:\s*المبارک)?|شوال|ذی\s*(?:القعدہ|الحج))\b"),
    re.compile(r"\b(?:عید\s*الفطر|عید\s*الاضحیٰ|یوم\s*عاشورہ)\b")
]

with open("v3/dev.jsonl", "r", encoding="utf-8") as f:
    dev = [json.loads(l) for l in f]

# 1. Before False Positives
fps_before = []
for idx, r in enumerate(dev):
    text = r["text"]
    gold_dates = [e for e in r["entities"] if e["label"] == "DATE"]
    preds = []
    for rx in OLD_DATE_REGEXES:
        for m in rx.finditer(text):
            preds.append({"start": m.start(), "end": m.end(), "text": m.group()})
    for p in preds:
        if not any(p["start"] == g["start"] and p["end"] == g["end"] for g in gold_dates):
            fps_before.append((idx, p["text"], text))

# 2. After False Positives
fps_after = []
for idx, r in enumerate(dev):
    text = r["text"]
    gold_dates = [e for e in r["entities"] if e["label"] == "DATE"]
    preds = [e for e in extract_regex_entities(text) if e["label"] == "DATE"]
    for p in preds:
        if not any(p["start"] == g["start"] and p["end"] == g["end"] for g in gold_dates):
            fps_after.append((idx, p["text"], text))

print(f"DATE False Positives on DEV: BEFORE = {len(fps_before)} -> AFTER = {len(fps_after)} (Reduction of {len(fps_before) - len(fps_after)} FPs!)")

# Save detailed before/after table
out_path = Path("reports/audit_final/date_fps_comparison.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("# DATE False Positives: Before vs After Strict Rule Hardening\n\n")
    f.write(f"- **Before False Positive Count:** {len(fps_before)}\n")
    f.write(f"- **After False Positive Count:** {len(fps_after)}\n")
    f.write(f"- **Net Spurious Matches Eliminated:** {len(fps_before) - len(fps_after)}\n\n")
    
    f.write("## 50 Before False Positives (Eliminated Bare Weekdays & Case-Insensitive Words)\n\n")
    f.write("| # | Dev Sent ID | Spurious Extracted String | Sentence Context |\n")
    f.write("| :-: | :-: | :--- | :--- |\n")
    for i, (idx, p_text, full_text) in enumerate(fps_before[:50]):
        clean_text = full_text.replace("\n", " ")[:90]
        f.write(f"| {i+1} | dev_{idx:03d} | `{p_text}` | {clean_text}... |\n")

    f.write("\n## 50 After False Positives (Remaining Real Calendar Mentions Not Tagged in Ground Truth)\n\n")
    f.write("| # | Dev Sent ID | Extracted String | Sentence Context |\n")
    f.write("| :-: | :-: | :--- | :--- |\n")
    for i, (idx, p_text, full_text) in enumerate(fps_after[:50]):
        clean_text = full_text.replace("\n", " ")[:90]
        f.write(f"| {i+1} | dev_{idx:03d} | `{p_text}` | {clean_text}... |\n")

print(f"Saved report to {out_path}")

import sys
import json
import csv

sys.stdout.reconfigure(encoding="utf-8")

print("================ FIRST 10 ROWS: .TXT OUTPUT (JSONL) ================")
with open("reports/final_eval/dry_run_txt/sample_50_hybrid.jsonl", "r", encoding="utf-8") as f:
    for i in range(10):
        line = f.readline()
        if not line:
            break
        r = json.loads(line)
        row_id = r.get("row_id")
        text_snippet = r.get("text", "")[:75]
        ents = [(e["label"], e["text"]) for e in r.get("entities", [])]
        print(f"[{i+1}] {row_id} | Text: \"{text_snippet}...\"")
        print(f"    Entities: {ents}")

print("\n================ FIRST 10 ROWS: .CSV OUTPUT (CSV SUMMARY) ================")
with open("reports/final_eval/dry_run_csv/sample_50_hybrid.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 10:
            break
        row_id = row.get("row_id")
        num_ents = row.get("num_entities")
        text_snippet = row.get("text", "")[:75]
        ents_json = row.get("entities_json", "")[:80]
        print(f"[{i+1}] {row_id} | Mentions: {num_ents} | Text: \"{text_snippet}...\"")
        print(f"    Entities JSON: {ents_json}...")

print("\n================ FIRST 10 ROWS: .CONLL OUTPUT (TOKEN + BIO TAG) ================")
with open("reports/final_eval/dry_run_conll/sample_50_hybrid.conll", "r", encoding="utf-8") as f:
    for i in range(10):
        line = f.readline()
        if not line:
            break
        print(f"[{i+1}] {line.strip()}")

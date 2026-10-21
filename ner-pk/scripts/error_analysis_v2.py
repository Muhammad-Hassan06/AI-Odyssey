import json

with open('student_pack_techfest/student_pack_techfest/student_pack/sample_test_v2_gold.jsonl', encoding='utf-8') as f:
    gold = {json.loads(l)['id']: json.loads(l) for l in f}
with open('student_pack_techfest/student_pack_techfest/student_pack/my_submission_v2.jsonl', encoding='utf-8') as f:
    pred = {json.loads(l)['id']: json.loads(l) for l in f}

print("=== MISSED ENTITIES (False Negatives) ===")
fn_count = 0
for sid, g in gold.items():
    p = pred.get(sid, {'entities': []})
    g_ents = {(e['start'], e['end'], e['label']): e for e in g['entities']}
    p_ents = {(e['start'], e['end'], e['label']): e for e in p['entities']}
    for k, e in g_ents.items():
        if k not in p_ents:
            fn_count += 1
            print(f"[{sid}] Missed: {e['label']} -> '{e.get('text', g['text'][e['start']:e['end']])}' | Full: \"{g['text']}\"")

print(f"\nTotal FN: {fn_count}")

print("\n=== FALSE POSITIVES (Model predicted something not in gold or wrong boundary/label) ===")
fp_count = 0
for sid, p in pred.items():
    g = gold.get(sid, {'entities': []})
    g_ents = {(e['start'], e['end'], e['label']): e for e in g['entities']}
    p_ents = {(e['start'], e['end'], e['label']): e for e in p['entities']}
    for k, e in p_ents.items():
        if k not in g_ents:
            fp_count += 1
            txt = g['text'][e['start']:e['end']]
            print(f"[{sid}] False Positive: {e['label']} -> '{txt}' | Full: \"{g['text']}\"")

print(f"\nTotal FP: {fp_count}")

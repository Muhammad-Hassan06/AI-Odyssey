import json

gold_path = 'student_pack_techfest/student_pack_techfest/student_pack/optional_self_check/sample_answer_key.jsonl'
pred_path = 'student_pack_techfest/student_pack_techfest/student_pack/my_submission_miss_official.jsonl'

with open(gold_path, encoding='utf-8') as f:
    gold = {json.loads(l)['id']: json.loads(l) for l in f}
with open(pred_path, encoding='utf-8') as f:
    pred = {json.loads(l)['id']: json.loads(l) for l in f}

print("=== MISSED ENTITIES (FN) ON MISS BENCHMARK ===")
fn_count = 0
for sid, g in gold.items():
    p = pred.get(sid, {'entities': []})
    g_ents = {(e['start'], e['end'], e['label']): e for e in g['entities']}
    p_ents = {(e['start'], e['end'], e['label']): e for e in p['entities']}
    for k, e in g_ents.items():
        if k not in p_ents:
            fn_count += 1
            txt = g['text'][e['start']:e['end']]
            print(f"[{sid}] Missed: {e['label']} -> '{txt}' | Full: \"{g['text']}\"")
print(f"Total FN: {fn_count}")

print("\n=== FALSE POSITIVES (FP) ON MISS BENCHMARK ===")
fp_count = 0
for sid, p in pred.items():
    g = gold.get(sid, {'entities': []})
    g_ents = {(e['start'], e['end'], e['label']): e for e in g['entities']}
    p_ents = {(e['start'], e['end'], e['label']): e for e in p['entities']}
    for k, e in p_ents.items():
        if k not in g_ents:
            fp_count += 1
            txt = g['text'][e['start']:e['end']]
            print(f"[{sid}] FP: {e['label']} -> '{txt}' | Full: \"{g['text']}\"")
print(f"Total FP: {fp_count}")

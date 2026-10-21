import json

gold_path = 'student_pack_techfest/student_pack_techfest/student_pack/sample_test_adv_gold.jsonl'
pred_path = 'student_pack_techfest/student_pack_techfest/student_pack/my_submission_adv.jsonl'

with open(gold_path, encoding='utf-8') as f:
    gold = {json.loads(l)['id']: json.loads(l) for l in f}
with open(pred_path, encoding='utf-8') as f:
    pred = {json.loads(l)['id']: json.loads(l) for l in f}

print("=== MISSED ENTITIES (FN) ON ADVERSARIAL BENCHMARK ===")
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

print("\n=== FALSE POSITIVES (FP) ON ADVERSARIAL BENCHMARK ===")
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

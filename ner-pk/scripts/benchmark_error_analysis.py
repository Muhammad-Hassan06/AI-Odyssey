import json
from pathlib import Path

BASE = Path("C:/Users/M Wasay/VS CODE ALL LANG FOLDERS/AI-Odyssey")
bench_path = BASE / "student_pack_techfest/student_pack_techfest/student_pack/sample_benchmark.jsonl"
gold_path = BASE / "student_pack_techfest/student_pack_techfest/student_pack/optional_self_check/sample_answer_key.jsonl"
pred_path = BASE / "student_pack_techfest/student_pack_techfest/student_pack/my_submission.jsonl"

with open(bench_path, encoding='utf-8') as f:
    benchmark = {d['id']: d['text'] for d in map(json.loads, f)}

with open(gold_path, encoding='utf-8') as f:
    gold = {d['id']: {(e['start'], e['end'], e['label'], benchmark[d['id']][e['start']:e['end']]) for e in d.get('entities', [])} for d in map(json.loads, f)}

with open(pred_path, encoding='utf-8') as f:
    pred = {d['id']: {(e['start'], e['end'], e['label'], benchmark[d['id']][e['start']:e['end']]) for e in d.get('entities', [])} for d in map(json.loads, f)}

print("======================================================================")
print("FALSE POSITIVES (Model predicted, but not in Gold)")
print("======================================================================")
for sid in sorted(gold.keys()):
    g_set = gold[sid]
    p_set = pred.get(sid, set())
    g_tuples = {(s, e, l) for (s, e, l, _) in g_set}
    fps = [e for e in p_set if (e[0], e[1], e[2]) not in g_tuples]
    if fps:
        print(f"\n{sid}: {benchmark[sid]}")
        for fp in sorted(fps):
            print(f"   [FP] {fp[2]}: '{fp[3]}' ({fp[0]}:{fp[1]})")

print("\n======================================================================")
print("FALSE NEGATIVES (In Gold, but Model missed)")
print("======================================================================")
for sid in sorted(gold.keys()):
    g_set = gold[sid]
    p_set = pred.get(sid, set())
    p_tuples = {(s, e, l) for (s, e, l, _) in p_set}
    fns = [e for e in g_set if (e[0], e[1], e[2]) not in p_tuples]
    if fns:
        print(f"\n{sid}: {benchmark[sid]}")
        for fn in sorted(fns):
            print(f"   [FN] {fn[2]}: '{fn[3]}' ({fn[0]}:{fn[1]})")

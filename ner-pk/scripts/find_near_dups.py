import sys
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

def get_5grams(text):
    words = text.lower().split()
    if len(words) < 5:
        return {text.lower()}
    return {" ".join(words[i:i+5]) for i in range(len(words)-4)}

def load_recs(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

train = load_recs("v2/train.jsonl")
bench = load_recs("v2/benchmark.jsonl")
dev = load_recs("v2/dev.jsonl")

inv = defaultdict(list)
t_grams = {}
for i, r in enumerate(train):
    g = get_5grams(r["text"])
    t_grams[i] = g
    for gram in g:
        inv[gram].append(i)

print("=== Checking Benchmark vs Train ===")
bench_dups = []
for b_idx, r in enumerate(bench):
    bg = get_5grams(r["text"])
    candidates = defaultdict(int)
    for gram in bg:
        for t_idx in inv.get(gram, []):
            candidates[t_idx] += 1
    for t_idx, count in candidates.items():
        tg = t_grams[t_idx]
        union = len(bg | tg)
        sim = count / union
        if sim > 0.75:
            print(f"BENCH-TRAIN DUP: sim={sim:.3f}")
            print(f"  Bench #{b_idx} (sentence_id={r.get('sentence_id')}, tier={r.get('tier')}): {r['text']}")
            print(f"  Train #{t_idx} (sentence_id={train[t_idx].get('sentence_id')}, tier={train[t_idx].get('tier')}): {train[t_idx]['text']}\n")
            bench_dups.append((b_idx, t_idx, r, train[t_idx], sim))

print(f"Total Bench vs Train near dups (>0.75): {len(bench_dups)}")


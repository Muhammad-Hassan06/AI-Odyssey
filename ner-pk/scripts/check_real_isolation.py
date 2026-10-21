import sys
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

def get_5grams(text):
    words = text.lower().split()
    if len(words) < 5:
        return {text.lower()}
    return {" ".join(words[i:i+5]) for i in range(len(words)-4)}

def is_synthetic(r):
    src = str(r.get('source', ''))
    art = str(r.get('article_id', ''))
    syn = r.get('synthetic')
    doc = str(r.get('doc_id', ''))
    sid = str(r.get('sentence_id', ''))
    if 'Synthetic' in src or 'synthetic' in doc or 'synthetic' in sid:
        return True
    if art.startswith('synthetic') or art.startswith('aug'):
        return True
    if syn is True:
        return True
    return False

train = [json.loads(l) for l in open('v3/train.jsonl', encoding='utf-8') if not is_synthetic(json.loads(l))]
dev = [json.loads(l) for l in open('v3/dev.jsonl', encoding='utf-8') if not is_synthetic(json.loads(l))]
bench = [json.loads(l) for l in open('v3/benchmark.jsonl', encoding='utf-8') if not is_synthetic(json.loads(l))]

print(f"REAL-ONLY: Train={len(train)}, Dev={len(dev)}, Bench={len(bench)}")

# Check document IDs (where present)
train_docs = {r.get('doc_id') or r.get('article_id') for r in train if (r.get('doc_id') or r.get('article_id'))}
dev_docs = {r.get('doc_id') or r.get('article_id') for r in dev if (r.get('doc_id') or r.get('article_id'))}
bench_docs = {r.get('doc_id') or r.get('article_id') for r in bench if (r.get('doc_id') or r.get('article_id'))}

print(f"Doc isolation Train & Dev: {len(train_docs & dev_docs)}")
if train_docs & dev_docs:
    print(f"  Overlap: {train_docs & dev_docs}")
print(f"Doc isolation Train & Bench: {len(train_docs & bench_docs)}")
if train_docs & bench_docs:
    print(f"  Overlap: {train_docs & bench_docs}")
print(f"Doc isolation Dev & Bench: {len(dev_docs & bench_docs)}")
if dev_docs & bench_docs:
    print(f"  Overlap: {dev_docs & bench_docs}")

# Check exact text
t_texts = {r['text'].strip().lower() for r in train}
d_texts = {r['text'].strip().lower() for r in dev}
b_texts = {r['text'].strip().lower() for r in bench}

print(f"Exact text Train & Dev: {len(t_texts & d_texts)}")
print(f"Exact text Train & Bench: {len(t_texts & b_texts)}")
print(f"Exact text Dev & Bench: {len(d_texts & b_texts)}")

# Check near-duplicates (>0.75 5-gram Jaccard)
inv = defaultdict(list)
t_grams = {}
for i, r in enumerate(train):
    g = get_5grams(r['text'])
    t_grams[i] = g
    for gram in g:
        inv[gram].append(i)

near_dups_tb = []
for b_idx, r in enumerate(bench):
    bg = get_5grams(r['text'])
    candidates = defaultdict(int)
    for gram in bg:
        for t_idx in inv.get(gram, []):
            candidates[t_idx] += 1
    for t_idx, count in candidates.items():
        tg = t_grams[t_idx]
        sim = count / len(bg | tg)
        if sim > 0.75:
            near_dups_tb.append((b_idx, t_idx, sim))

print(f"Near-duplicates Train & Bench (>0.75): {len(near_dups_tb)}")

near_dups_td = []
for d_idx, r in enumerate(dev):
    dg = get_5grams(r['text'])
    candidates = defaultdict(int)
    for gram in dg:
        for t_idx in inv.get(gram, []):
            candidates[t_idx] += 1
    for t_idx, count in candidates.items():
        tg = t_grams[t_idx]
        sim = count / len(dg | tg)
        if sim > 0.75:
            near_dups_td.append((d_idx, t_idx, sim))

print(f"Near-duplicates Train & Dev (>0.75): {len(near_dups_td)}")

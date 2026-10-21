import sys
import json
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

for split in ['train', 'dev', 'benchmark']:
    with open(f'v3/{split}.jsonl', 'r', encoding='utf-8') as f:
        print(f'=== INSPECTING {split} ===')
        combos = Counter()
        examples = {}
        for i, line in enumerate(f):
            r = json.loads(line)
            src = r.get('source')
            tier = r.get('tier')
            syn = r.get('synthetic')
            doc = r.get('doc_id')
            key = (src, tier, syn, doc is not None)
            combos[key] += 1
            if key not in examples:
                examples[key] = (r.get('sentence_id'), r.get('text')[:90], r.get('domain'))
        for k, v in combos.most_common():
            sid, txt, dom = examples[k]
            print(f'Count: {v:5d} | key: {k} | sid: {sid} | dom: {dom}')
            print(f'   Sample: {txt}')

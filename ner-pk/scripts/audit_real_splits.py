import sys
import json
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

for split in ['train', 'dev', 'benchmark']:
    with open(f'v3/{split}.jsonl', 'r', encoding='utf-8') as f:
        recs = [json.loads(line) for line in f]
    print(f"=== v3/{split}.jsonl (Total: {len(recs)}) ===")
    
    # Classify each record
    real_count = 0
    synth_count = 0
    reasons = Counter()
    
    for r in recs:
        src = str(r.get('source', ''))
        art = str(r.get('article_id', ''))
        syn = r.get('synthetic')
        doc = str(r.get('doc_id', ''))
        tier = str(r.get('tier', ''))
        
        # Criteria for synthetic:
        # 1. source mentions "Synthetic"
        # 2. doc_id or sentence_id starts with "synthetic"
        # 3. article_id starts with "synthetic" or "aug"
        # 4. synthetic is True
        if 'Synthetic' in src or 'synthetic' in doc or 'synthetic' in str(r.get('sentence_id', '')):
            synth_count += 1
            reasons['synthetic_source_or_doc'] += 1
        elif art.startswith('synthetic'):
            synth_count += 1
            reasons['article_synthetic'] += 1
        elif art.startswith('aug'):
            synth_count += 1
            reasons['article_augmented'] += 1
        elif syn is True:
            synth_count += 1
            reasons['synthetic_flag_true'] += 1
        else:
            real_count += 1
            # What kind of real text?
            if 'Wikipedia' in src:
                reasons['real_wikipedia'] += 1
            elif 'urdu' in doc.lower() or 'Urdu' in src:
                reasons['real_urdu_wiki'] += 1
            elif art:
                prefix = art.split('_')[0]
                reasons[f'real_news_{prefix}'] += 1
            else:
                reasons['real_scraped_no_art'] += 1
                
    print(f"  Real sentences: {real_count}")
    print(f"  Synthetic sentences: {synth_count}")
    print("  Breakdown:")
    for k, v in reasons.most_common():
        print(f"    {k}: {v}")

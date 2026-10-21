"""
Build v3 data files from v2 data files:
1. Map GOVERNMENT_BODIES -> GOVERNMENT_BODY across entities and bio_tags.
2. Repair corrupt entities (start < 0 or empty text): remove bad entities, reset bio_tags to 'O'.
3. Remove near-duplicate sentence (Train #213 which duplicates Benchmark #253).
4. Normalize tiers to strict 4-tier schema (GOLD, SILVER-HC, SILVER, SYNTHETIC).
   - In dev and benchmark: convert false 'gold' to 'SILVER' (since 0 human-gold sentences).
   - In train: convert 'augmented', 'negative' to 'SYNTHETIC'; scraped real text to 'SILVER'.
5. Rebuild BIO tags to guarantee 100% valid IOB2 transitions.
6. Export JSONL and CoNLL files into v3/.
"""

import os
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ALLOWED_20_LABELS = {
    "PERSON",
    "CITY",
    "PROVINCE_REGION",
    "COUNTRY",
    "LANDMARK_FACILITY",
    "GOVERNMENT_BODY",
    "POLITICAL_PARTY",
    "ORGANIZATION",
    "EDUCATIONAL_INSTITUTION",
    "COURT_LEGAL_BODY",
    "LAW_ACT",
    "EVENT",
    "MEDIA_OUTLET",
    "SPORTS_TEAM",
    "DATE",
    "TIME",
    "MONEY",
    "PERCENT",
    "PHONE_NUMBER",
    "ID_NUMBER",
}

def rebuild_bio_tags(text, tokens, entities):
    """
    Rebuilds strict IOB2 bio_tags for tokens matching character span entities.
    """
    if not tokens:
        return []
    
    # Locate token character spans in text
    token_spans = []
    cursor = 0
    for tok in tokens:
        pos = text.find(tok, cursor)
        if pos == -1:
            # Fallback if whitespace/normalization difference
            pos = cursor
        token_spans.append((pos, pos + len(tok)))
        cursor = pos + len(tok)
    
    bio_tags = ["O"] * len(tokens)
    
    # Sort entities by start
    sorted_entities = sorted(entities, key=lambda e: (e["start"], e["end"]))
    
    for ent in sorted_entities:
        label = ent["label"]
        e_start = ent["start"]
        e_end = ent["end"]
        
        first_token = True
        for t_idx, (t_start, t_end) in enumerate(token_spans):
            # Overlap check
            if max(t_start, e_start) < min(t_end, e_end):
                if first_token:
                    bio_tags[t_idx] = f"B-{label}"
                    first_token = False
                else:
                    bio_tags[t_idx] = f"I-{label}"
                    
    # Strict validation of BIO sequence
    prev_tag = "O"
    for t_idx, tag in enumerate(bio_tags):
        if tag.startswith("I-"):
            curr_class = tag[2:]
            if prev_tag == "O" or prev_tag[2:] != curr_class:
                bio_tags[t_idx] = f"B-{curr_class}"
        prev_tag = bio_tags[t_idx]
        
    return bio_tags

def process_file(in_path, out_jsonl_path, out_conll_path, split_name):
    print(f"\nProcessing {split_name} from {in_path}...")
    repaired_count = 0
    gov_bodies_remapped = 0
    removed_near_dups = 0
    out_records = []
    
    with open(in_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            rec = json.loads(line)
            text = rec["text"]
            entities = rec.get("entities", [])
            tokens = rec.get("tokens", [])
            tier = rec.get("tier", "SILVER")
            
            # Check near-duplicate in train
            if split_name == "train" and "Rock art and petroglyphs" in text and "50,000 pieces of rock art" in text and rec.get("sentence_id") is None:
                print(f"  Removing near-duplicate Train record #{idx}: '{text[:70]}...'")
                removed_near_dups += 1
                continue
                
            # Check for corrupt entities (start < 0 or empty text)
            corrupt = [e for e in entities if e.get("start", 0) < 0 or not str(e.get("text", "")).strip()]
            if corrupt:
                repaired_count += 1
                # Filter out corrupt entities
                entities = [e for e in entities if e.get("start", 0) >= 0 and str(e.get("text", "")).strip()]
                
            # Remap GOVERNMENT_BODIES -> GOVERNMENT_BODY
            clean_entities = []
            for ent in entities:
                lbl = ent["label"]
                if lbl == "GOVERNMENT_BODIES":
                    lbl = "GOVERNMENT_BODY"
                    gov_bodies_remapped += 1
                if lbl not in ALLOWED_20_LABELS:
                    raise ValueError(f"Unknown label '{lbl}' at {split_name} #{idx}")
                clean_entities.append({
                    "start": ent["start"],
                    "end": ent["end"],
                    "label": lbl,
                    "text": ent["text"]
                })
            
            # Normalize Tier
            if split_name in ("dev", "benchmark"):
                # Dev and benchmark may only contain real text; no human gold verified
                clean_tier = "SILVER"
            else:
                if tier in ("augmented", "synthetic", "negative", "SYNTHETIC"):
                    clean_tier = "SYNTHETIC"
                elif tier in ("gold", "GOLD"):
                    clean_tier = "SILVER" # honest silver
                else:
                    clean_tier = "SILVER"
            
            # Rebuild BIO tags
            bio_tags = rebuild_bio_tags(text, tokens, clean_entities)
            
            rec["entities"] = clean_entities
            rec["bio_tags"] = bio_tags
            rec["tier"] = clean_tier
            out_records.append(rec)
            
    # Write JSONL
    os.makedirs(os.path.dirname(out_jsonl_path), exist_ok=True)
    with open(out_jsonl_path, "w", encoding="utf-8") as f:
        for r in out_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    # Write CoNLL
    with open(out_conll_path, "w", encoding="utf-8") as f:
        for r in out_records:
            for tok, tag in zip(r["tokens"], r["bio_tags"]):
                f.write(f"{tok} {tag}\n")
            f.write("\n")
            
    print(f"  Total records written: {len(out_records)}")
    print(f"  Corrupt sentences repaired: {repaired_count}")
    print(f"  GOVERNMENT_BODIES remapped: {gov_bodies_remapped}")
    print(f"  Near duplicates removed: {removed_near_dups}")
    
    return {
        "split": split_name,
        "total": len(out_records),
        "repaired": repaired_count,
        "remapped": gov_bodies_remapped,
        "removed_dups": removed_near_dups
    }

def main():
    v3_dir = Path("v3")
    v3_dir.mkdir(exist_ok=True)
    
    stats = []
    stats.append(process_file("v2/train.jsonl", v3_dir / "train.jsonl", v3_dir / "train.conll", "train"))
    stats.append(process_file("v2/dev.jsonl", v3_dir / "dev.jsonl", v3_dir / "dev.conll", "dev"))
    stats.append(process_file("v2/benchmark.jsonl", v3_dir / "benchmark.jsonl", v3_dir / "benchmark.conll", "benchmark"))
    
    print("\nSummary of v3 Data Creation:")
    for s in stats:
        print(f"  {s['split']}: {s['total']} sentences (Repaired: {s['repaired']}, Remapped: {s['remapped']}, Removed: {s['removed_dups']})")

if __name__ == "__main__":
    main()

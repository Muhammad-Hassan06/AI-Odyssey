#!/usr/bin/env python3
"""TechFest NER Challenge: create (and check) your submission file.

HOW TO USE
  1. Edit ONLY the two sections marked  "EDIT HERE"  (load your model, fill in predict()).
  2. Create your submission:
         python make_submission.py --input sample_benchmark.jsonl --output submission.jsonl
  3. Check a file without creating one:
         python make_submission.py --check submission.jsonl --input sample_benchmark.jsonl

The input file has one sentence per line:   {"id": "...", "text": "..."}
The submission has one line per sentence:   {"id": "...", "entities": [{"start": 0, "end": 5, "label": "CITY"}]}
start/end are CHARACTER positions in the sentence text (end is exclusive): text[start:end] is the entity.

LABELS ARE STRICT: every label must be exactly one of the 20 official labels below (upper case, same spelling).
Labels such as PER, ORG, LOC or B-CITY are NOT accepted. If your model outputs any other label, no
submission file is created and the script tells you which labels were wrong.
"""
import argparse, collections, json, sys

LABELS = ["PERSON", "CITY", "PROVINCE_REGION", "COUNTRY", "LANDMARK_FACILITY",
          "GOVERNMENT_BODY", "POLITICAL_PARTY", "ORGANIZATION", "EDUCATIONAL_INSTITUTION",
          "COURT_LEGAL_BODY", "LAW_ACT", "EVENT", "MEDIA_OUTLET", "SPORTS_TEAM", "DATE",
          "TIME", "MONEY", "PERCENT", "PHONE_NUMBER", "ID_NUMBER"]


# =========================================================================
# EDIT HERE (1/2): load your model once.
# =========================================================================
def load_model():
    import sys
    from pathlib import Path
    ner_pk_dir = Path(__file__).resolve().parent.parent.parent.parent / "ner-pk"
    if str(ner_pk_dir) not in sys.path:
        sys.path.insert(0, str(ner_pk_dir))
    from predict import UnifiedNERPredictor
    model_dir = str(ner_pk_dir / "models" / "v5")
    predictor = UnifiedNERPredictor(model_dir=model_dir, mode="hybrid")
    return predictor


# =========================================================================
# EDIT HERE (2/2): return the entities your model finds in ONE sentence.
# Return a list of dicts with start, end, label (character positions in `text`).
# Each label MUST be one of the 20 official labels in LABELS above, spelled exactly the same.
# Helper functions below can convert common model outputs for you.
# =========================================================================
def predict(model, text):
    ents = model.predict_single(text)
    return [{"start": e["start"], "end": e["end"], "label": e["label"]} for e in ents]


# ----------------------------------------------------------------- helpers
def spans_from_hf(outputs):
    """Convert a Hugging Face token-classification pipeline output (aggregation_strategy='simple')."""
    return [{"start": o["start"], "end": o["end"], "label": o.get("entity_group") or o.get("entity", "")}
            for o in outputs]


def spans_from_bio(text, tokens, tags):
    """Convert word tokens + BIO tags (e.g. 'B-CITY', 'I-CITY', 'O') into character spans."""
    spans, cursor, cur = [], 0, None
    for tok, tag in zip(tokens, tags):
        i = text.find(tok, cursor)
        if i < 0:
            continue
        j = i + len(tok)
        cursor = j
        if tag == "O":
            if cur:
                spans.append(cur)
                cur = None
            continue
        prefix, _, lab = tag.partition("-")
        if prefix == "B" or cur is None or cur["label"] != lab:
            if cur:
                spans.append(cur)
            cur = {"start": i, "end": j, "label": lab}
        else:
            cur["end"] = j
    if cur:
        spans.append(cur)
    return spans


def clean(text, raw, stats):
    """Reject unofficial labels, drop invalid-offset or overlapping spans, return a sorted list."""
    out = []
    for e in raw:
        if isinstance(e, (tuple, list)):
            e = {"start": e[0], "end": e[1], "label": e[2]}
        lab = e["label"]
        s, t = int(e["start"]), int(e["end"])
        if lab not in LABELS:
            stats["bad_label"][lab] += 1
            continue
        if not (0 <= s < t <= len(text)):
            stats["bad_offsets"] += 1
            continue
        # trim spaces at the edges (some tokenizers include a leading space in the span)
        while s < t and text[s].isspace():
            s += 1
        while t > s and text[t - 1].isspace():
            t -= 1
        if s >= t:
            stats["bad_offsets"] += 1
            continue
        out.append({"start": s, "end": t, "label": lab})
    out.sort(key=lambda x: (x["start"], -(x["end"])))
    final, prev_end = [], 0
    for e in out:
        if e["start"] < prev_end:
            stats["overlap"] += 1
            continue
        final.append(e)
        prev_end = e["end"]
    return final


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def check(sub_path, input_path):
    texts = {d["id"]: d["text"] for d in read_jsonl(input_path)}
    sub = read_jsonl(sub_path)
    problems, seen = [], set()
    for d in sub:
        sid = d.get("id")
        if sid not in texts:
            problems.append(f"unknown id: {sid}")
            continue
        if sid in seen:
            problems.append(f"duplicate id: {sid}")
        seen.add(sid)
        prev = 0
        ents = d.get("entities", [])
        if not all(isinstance(e, dict) and isinstance(e.get("start"), int) and isinstance(e.get("end"), int)
                   for e in ents):
            problems.append(f"{sid}: each entity needs integer start and end")
            continue
        for e in sorted(ents, key=lambda x: x["start"]):
            if e.get("label") not in LABELS:
                problems.append(f"{sid}: invalid label {e.get('label')!r}")
            if not (0 <= e["start"] < e["end"] <= len(texts[sid])):
                problems.append(f"{sid}: offsets out of range {e}")
            if e["start"] < prev:
                problems.append(f"{sid}: overlapping entities")
            prev = max(prev, e["end"])
    missing = set(texts) - seen
    if missing:
        problems.append(f"{len(missing)} sentences missing from the submission (they will count as 'no entities')")
    n_ent = sum(len(d.get("entities", [])) for d in sub)
    print(f"Checked {len(sub)} lines, {n_ent} entities.")
    if problems:
        print("PROBLEMS FOUND:")
        for p in problems[:30]:
            print("  -", p)
        if len(problems) > 30:
            print(f"  ... and {len(problems) - 30} more")
        return 1
    print("OK: submission format is valid.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="input .jsonl with id and text")
    ap.add_argument("--output", help="where to write your submission .jsonl")
    ap.add_argument("--check", help="only check this existing submission file")
    a = ap.parse_args()
    if a.check:
        sys.exit(check(a.check, a.input))
    if not a.output:
        ap.error("--output is required unless you use --check")
    model = load_model()
    stats = {"bad_label": collections.Counter(), "bad_offsets": 0, "overlap": 0}
    rows = read_jsonl(a.input)
    results = [{"id": d["id"], "entities": clean(d["text"], predict(model, d["text"]), stats)} for d in rows]
    if stats["bad_label"]:
        print("ERROR: your model produced labels that are NOT in the official 20. No submission file was created.")
        for lab, n in stats["bad_label"].most_common():
            print(f"  - {lab!r}: {n} time(s)")
        print("Fix your model or predict() so every label is exactly one of:")
        print("  " + ", ".join(LABELS))
        sys.exit(1)
    with open(a.output, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(results)} lines to {a.output}")
    if stats["bad_offsets"] or stats["overlap"]:
        print(f"Dropped: {stats['bad_offsets']} with bad offsets, {stats['overlap']} overlapping.")
    sys.exit(check(a.output, a.input))


if __name__ == "__main__":
    main()

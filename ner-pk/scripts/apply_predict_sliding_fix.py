import os

path = os.path.join(os.path.dirname(__file__), "..", "predict.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """                if tag.startswith("B-"):
                    if curr_ent:
                        all_candidate_spans.append(curr_ent)
                    lbl = tag[2:]
                    curr_ent = {
                        "text": text[start_char:end_char],
                        "start": int(start_char),
                        "end": int(end_char),
                        "label": lbl,
                        "confidences": [conf]
                    }
                elif tag.startswith("I-"):
                    lbl = tag[2:]
                    if curr_ent and curr_ent["label"] == lbl:
                        curr_ent["end"] = int(end_char)
                        curr_ent["text"] = text[curr_ent["start"]:int(end_char)]
                        curr_ent["confidences"].append(conf)
                    else:
                        if curr_ent:
                            all_candidate_spans.append(curr_ent)
                        curr_ent = {
                            "text": text[start_char:end_char],
                            "start": int(start_char),
                            "end": int(end_char),
                            "label": lbl,
                            "confidences": [conf]
                        }
                else:
                    if curr_ent:
                        all_candidate_spans.append(curr_ent)
                        curr_ent = None"""

new_block = """                lbl = tag[2:] if tag.startswith(("B-", "I-")) else "O"

                # Subword continuation: if adjacent to active entity with same label, merge seamlessly
                if curr_ent and curr_ent["label"] == lbl and (start_char == curr_ent["end"] or tag.startswith("I-")):
                    curr_ent["end"] = int(end_char)
                    curr_ent["text"] = text[curr_ent["start"]:int(end_char)]
                    curr_ent["confidences"].append(conf)
                elif tag.startswith("B-"):
                    if curr_ent:
                        all_candidate_spans.append(curr_ent)
                    curr_ent = {
                        "text": text[start_char:end_char],
                        "start": int(start_char),
                        "end": int(end_char),
                        "label": lbl,
                        "confidences": [conf]
                    }
                elif tag.startswith("I-"):
                    if curr_ent:
                        all_candidate_spans.append(curr_ent)
                    curr_ent = {
                        "text": text[start_char:end_char],
                        "start": int(start_char),
                        "end": int(end_char),
                        "label": lbl,
                        "confidences": [conf]
                    }
                else:
                    if curr_ent:
                        all_candidate_spans.append(curr_ent)
                        curr_ent = None"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated predict.py sliding window logic successfully!")
else:
    print("Error: old_block not found in predict.py!")

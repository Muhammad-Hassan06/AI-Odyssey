import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
preannotate_path = os.path.join(base_dir, "src", "preannotate.py")
postprocess_path = os.path.join(base_dir, "src", "postprocess.py")

# 1. Update src/preannotate.py
with open(preannotate_path, "r", encoding="utf-8") as f:
    pre_code = f.read()

old_urdu_tokens = "URDU_POSTPOSITIONS = {'کا', 'کی', 'کے', 'نے', 'کو', 'سے', 'میں', 'پر', 'تک', 'اور', 'یا'}"
new_urdu_tokens = """URDU_NON_NAME_TOKENS = {
        'کا', 'کی', 'کے', 'نے', 'کو', 'سے', 'میں', 'پر', 'تک', 'اور', 'یا',
        'عدالت', 'پولیس', 'تھانہ', 'جیل', 'حکومت', 'اسمبلی', 'وزارت', 'دفتر',
        'کمیشن', 'بینک', 'بورڈ', 'کمیٹی', 'پارٹی', 'کوٹہ', 'فیصلہ', 'پیش'
    }"""

pre_code = pre_code.replace(old_urdu_tokens, new_urdu_tokens)
pre_code = pre_code.replace("if t in URDU_POSTPOSITIONS", "if t in URDU_NON_NAME_TOKENS")

with open(preannotate_path, "w", encoding="utf-8") as f:
    f.write(pre_code)

print("Updated preannotate.py with URDU_NON_NAME_TOKENS!")

# 2. Update src/postprocess.py
with open(postprocess_path, "r", encoding="utf-8") as f:
    post_code = f.read()

percent_check = """    # 2.5 PERCENT must contain % or percent or فیصد
    if lbl == "PERCENT":
        if not ("%" in span or "percent" in span_lower or "per cent" in span_lower or "فیصد" in span):
            return True"""

if 'if lbl == "PERCENT":' not in post_code:
    post_code = post_code.replace(
        'if lbl in FALSE_POSITIVE_WORDS:',
        percent_check + '\n\n    if lbl in FALSE_POSITIVE_WORDS:'
    )

with open(postprocess_path, "w", encoding="utf-8") as f:
    f.write(post_code)

print("Updated postprocess.py with PERCENT guard!")

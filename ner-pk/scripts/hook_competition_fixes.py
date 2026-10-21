with open('predict.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import
old_import = "from src.postprocess import postprocess_entities, hybrid_merge_predictions"
new_import = "from src.postprocess import postprocess_entities, hybrid_merge_predictions\nfrom src.competition_fixes import apply_competition_fixes"
assert old_import in content, "old_import not found"
content = content.replace(old_import, new_import, 1)

# 2. Add apply_competition_fixes to predict_single
old_predict = """        # 3. Conservative Hybrid mode (default)
        rule_ents = preannotate_sentence(text)
        merged = hybrid_merge_predictions(model_ents, rule_ents, len(text))
        final_ents = postprocess_entities(text, merged)
        return self._filter_schema(final_ents, text)"""

new_predict = """        # 3. Conservative Hybrid mode (default)
        rule_ents = preannotate_sentence(text)
        merged = hybrid_merge_predictions(model_ents, rule_ents, len(text))
        final_ents = postprocess_entities(text, merged)
        competition_ents = apply_competition_fixes(text, final_ents)
        return self._filter_schema(competition_ents, text)"""

assert old_predict in content, "old_predict not found"
content = content.replace(old_predict, new_predict, 1)

with open('predict.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: hooked apply_competition_fixes into predict.py")

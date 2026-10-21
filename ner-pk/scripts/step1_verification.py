import os
import sys
import json
import hashlib

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.infer import PakistaniNERPredictor
import app.app as app_mod

final_dir = os.path.join(base_dir, "models", "final")
safetensor_path = os.path.join(final_dir, "model.safetensors")

print("==================================================")
print("STEP 1: CHECKPOINT VERIFICATION REPORT")
print("==================================================")

# 1. File verification
files = sorted(os.listdir(final_dir))
print(f"Files in models/final/: {files}")

size_bytes = os.path.getsize(safetensor_path)
h = hashlib.sha256()
with open(safetensor_path, "rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
        h.update(chunk)
sha256 = h.hexdigest()

print(f"model.safetensors Size:   {size_bytes:,} bytes ({size_bytes / (1024**3):.2f} GB)")
print(f"model.safetensors SHA256: {sha256}")

# 2. Config & id2label verification
cfg = json.load(open(os.path.join(final_dir, "config.json"), encoding="utf-8"))
id2label = cfg.get("id2label", {})
print(f"Number of output labels:  {len(id2label)}")

from src.constants import BIO_LABELS
allowed_bio = set(BIO_LABELS)
labels = [id2label[str(i)] for i in range(len(id2label))] if str(0) in id2label else list(id2label.values())
outside_labels = [l for l in labels if l not in allowed_bio]

print(f"Labels outside 20-class BIO schema: {outside_labels if outside_labels else 'NONE (100% compliant)'}")

# 3. App status verification
print("\n--- APP LOADING VERIFICATION ---")
print(f"app.model_available:      {app_mod.model_available}")
print(f"app.MODEL_STATUS_BANNER:  {app_mod.MODEL_STATUS_BANNER}")
has_fallback_banner = "NOTICE: No trained transformer checkpoint found" in app_mod.MODEL_STATUS_BANNER
print(f"Fallback Warning Banner Displayed: {has_fallback_banner} (False is EXPECTED)")

# 4. Predictors initialization (reuse app_mod to avoid redundant weight reloading)
p_model = app_mod.neural_predictor
p_hybrid = app_mod.hybrid_predictor
print(f"p_model device: {p_model.device}, mode: {p_model.mode}, weights loaded: {p_model.model is not None}")

# 5. 10 Diverse Sentences Sanity Test
test_sentences = [
    "A division bench of the Supreme Court of Pakistan convened in Islamabad on Monday.",
    "Prime Minister Shehbaz Sharif met with Chinese Premier Li Qiang in Beijing.",
    "سندھ ہائیکورٹ نے کراچی میں بلدیاتی انتخابات کے حوالے سے الیکشن کمیشن کو نوٹس جاری کر دیا۔",
    "Lahore Qalandars defeated Multan Sultans by 5 wickets in the Pakistan Super League final at Gaddafi Stadium.",
    "STATE BANK OF PAKISTAN HIKES POLICY RATE TO 17.5 PERCENT IN KARACHI.",
    "The Federal Board of Revenue collected Rs 850 billion in taxes in October 2025.",
    "National Database and Registration Authority issued CNIC 35201-7654321-9 to the citizen.",
    "Please contact the emergency response cell at +92-300-1234567 or 042-35871234.",
    "The hearing at the Peshawar High Court was adjourned until 11:30 AM.",
    "Allama Iqbal Open University in Islamabad announced new admissions for the spring semester."
]

print("\n--- 10 DIVERSE SENTENCE PREDICTION RESULTS ---")
results = []
for idx, s in enumerate(test_sentences, 1):
    m_ents = p_model.predict(s)
    h_ents = p_hybrid.predict(s)
    m_summary = [(e["label"], e["text"]) for e in m_ents]
    h_summary = [(e["label"], e["text"]) for e in h_ents]
    print(f"\n[{idx}] TEXT: {s}")
    print(f"  MODEL-ONLY: {m_summary}")
    print(f"  HYBRID:     {h_summary}")
    results.append({
        "index": idx,
        "text": s,
        "model_only": m_summary,
        "hybrid": h_summary
    })

# Save results for documentation
out_path = os.path.join(base_dir, "reports", "audit_final", "step1_sanity_test.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "sha256": sha256,
        "size_bytes": size_bytes,
        "labels": labels,
        "outside_labels": outside_labels,
        "app_status_banner": app_mod.MODEL_STATUS_BANNER,
        "sanity_predictions": results
    }, f, indent=2, ensure_ascii=False)

print(f"\nSaved Step 1 report to {out_path}")

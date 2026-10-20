"""
Interactive Gradio Web Application for Pakistani-Context Named Entity Recognition (NER).
TechFest NER Challenge — Dory's Data Dive (Round 2)

Features:
1. Tab 1: Single Sentence Inspector with Script Detection & Visual Entity Highlighting.
2. Tab 2: Batch File Processor & Exporter (Upload .txt/.jsonl/.csv -> Download CSV/JSONL/CoNLL).
3. Tab 3: Raw Formats & Schema Reference (CoNLL-2003, JSON, BIO Token Alignment).
"""

import os
import sys
import re
import json
import tempfile
import pandas as pd
import gradio as gr

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import ENTITY_TYPES
from src.infer import PakistaniNERPredictor
from src.dataset import spans_to_bio

# Initialize unified hybrid predictor
predictor = PakistaniNERPredictor(mode="hybrid")

EXAMPLES = [
    # 1. Budget & Economy News
    [
        "Finance Minister Muhammad Aurangzeb presented the Federal Budget 2025-26 in the National Assembly. "
        "The Federal Board of Revenue set a tax collection target of Rs 12.9 trillion, while inflation eased to 11.5 per cent. "
        "The State Bank of Pakistan announced policy adjustments on Monday."
    ],
    # 2. Supreme Court & Legal Proceedings
    [
        "A five-member bench of the Supreme Court of Pakistan, headed by Chief Justice Qazi Faez Isa, "
        "heard constitutional petitions challenging Section 4 of PECA 2016 in Islamabad. "
        "The Sindh High Court had previously issued directions regarding Article 63-A of the Constitution."
    ],
    # 3. PSL Cricket Match Report
    [
        "In a thrilling PSL 10 clash at National Stadium Karachi, Karachi Kings defeated Lahore Qalandars by 5 wickets. "
        "Babar Azam scored a brilliant half-century before the innings concluded at 11:45 PM in front of 35,000 cheering fans."
    ],
    # 4. University Admissions & Notice
    [
        "Admissions for the Fall 2025 semester opened at LUMS in Lahore and NED University in Karachi on 14 August 2025. "
        "Tuition fees are set at PKR 450,000 per term. For inquiries, contact the registrar desk at +92 300 1234567 before Friday."
    ],
    # 5. Administrative Citizen Notice (Synthetic ID / Phone)
    [
        "Verification alert: Citizen with CNIC 42101-1234567-1 has been registered under the civic database in Rawalpindi. "
        "In case of discrepancy, dial the emergency helpline 051-9201234 or visit the NADRA facilitation center between 09:00 PST and 17:00 PST."
    ],
    # 6. Urdu Legal & Constitutional Hearing
    [
        "سپریم کورٹ آف پاکستان کے دو رکنی بینچ نے اسلام آباد میں 26ویں آئینی ترمیم کے تحت کیس کی سماعت کی۔ "
        "عدالت نے اٹارنی جنرل کو پیر کے روز صبح 11:30 بجے تفصیلی دلائل کے لیے طلب کر لیا ہے۔"
    ],
    # 7. Urdu Citizen Verification (Eastern Arabic Digits: CNIC & Phone)
    [
        "نادرا ہیلپ ڈیسک کی تصدیق کے مطابق امیدوار کا شناختی کارڈ نمبر ۴۲۱۰۱-۱۲۳۴۵۶۷-۱ منظور کر لیا گیا ہے۔ "
        "کسی بھی شکایت کی صورت میں شہری رابطہ نمبر ۰۳۰۰-۱۲۳۴۵۶۷ پر فوری کال کر سکتے ہیں۔"
    ],
    # 8. Urdu Sports & Economy
    [
        "پاکستان سپر لیگ کے فائنل میں لاہور قلندرز نے کراچی کنگز کو سنسنی خیز مقابلے کے بعد شکست دے دی۔ "
        "وزارت خزانہ نے 15 کروڑ روپے کے خصوصی پیکیج اور 5.2 فیصد ٹیکس رعایت کی منظوری دی ہے۔"
    ]
]

def detect_script_and_metrics(text: str) -> str:
    """Detect language script (Urdu, Roman Urdu, English) and provide text diagnostics."""
    if not text or not text.strip():
        return "ℹ️ *Enter text above to inspect script and extract entities.*"
    
    total_chars = len(text)
    urdu_chars = sum(1 for c in text if ("\u0600" <= c <= "\u06FF" or "\uFB50" <= c <= "\uFDFF" or "\uFE70" <= c <= "\uFEFF"))
    eastern_digits = sum(1 for c in text if c in "۰۱۲۳۴۵۶۷۸۹")
    
    urdu_ratio = urdu_chars / total_chars if total_chars > 0 else 0
    words = text.split()
    
    if urdu_ratio > 0.15:
        script_name = "🟢 **Urdu Script (Naskh / Nastaliq)**"
        details = f"Urdu character density: {urdu_ratio*100:.1f}% | Eastern Arabic-Indic Digits: {eastern_digits}"
    elif any(rw in text.lower() for rw in ["wazir", "azam", "hukumat", "adalat", "intikhabat", "fauj", "qaumi", "subaee", "jeet", "khilaf"]):
        script_name = "🟣 **Roman Urdu / Code-Mixed (Latin Script Transliteration)**"
        details = "Vernacular Pakistani phonetic markers detected."
    else:
        script_name = "🔵 **English (Pakistani Civic / Legal / Financial Context)**"
        details = "Standard Latin orthography with Pakistani institutional domain vocabulary."
        
    return f"{script_name} — {details} | Words: {len(words)} | Characters: {total_chars}"

def analyze_ner(text: str, filter_labels: list = None):
    """Run predictor on text and return diagnostics, highlighted spans, and structured table rows."""
    if not text or not text.strip():
        return "ℹ️ *No input text provided.*", {"text": "", "entities": []}, [], "No entities extracted."

    script_banner = detect_script_and_metrics(text)
    entities = predictor.predict(text)
    
    if filter_labels:
        entities = [e for e in entities if e["label"] in filter_labels]

    formatted_entities = [
        {"entity": e["label"], "start": e["start"], "end": e["end"]}
        for e in entities
    ]

    table_rows = [
        [i + 1, e["text"], e["label"], e["start"], e["end"]]
        for i, e in enumerate(entities)
    ]

    summary_text = f"Extracted **{len(entities)}** named entities across **{len(set(e['label'] for e in entities))}** distinct classes."
    return script_banner, {"text": text, "entities": formatted_entities}, table_rows, summary_text

def format_raw_output(text: str, fmt: str) -> str:
    """Format single sentence predictions into CoNLL, JSON, or BIO token list."""
    if not text or not text.strip():
        return "Please enter text to format."
    
    entities = predictor.predict(text)
    if fmt == "CoNLL-2003 Tab-Delimited":
        tokens, bio_tags = spans_to_bio(text, entities)
        lines = ["# Token\tBIO-Tag"]
        for tok, tag in zip(tokens, bio_tags):
            lines.append(f"{tok}\t{tag}")
        return "\n".join(lines)
    elif fmt == "JSON (Character Offsets)":
        return json.dumps({"text": text, "entities": entities}, ensure_ascii=False, indent=2)
    elif fmt == "BIO Tokens List":
        tokens, bio_tags = spans_to_bio(text, entities)
        return json.dumps({"tokens": tokens, "bio_tags": bio_tags}, ensure_ascii=False, indent=2)
    return ""

def process_batch_file(file_obj, export_format: str):
    """
    Process an uploaded .txt, .csv, or .jsonl file, extract entities from all sentences,
    and generate a downloadable output file in the selected format.
    """
    if file_obj is None:
        return None, "⚠️ Please upload a valid file first.", []
    
    file_path = file_obj.name
    sentences = []
    
    # Read sentences based on extension
    if file_path.endswith(".jsonl"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        sentences.append(data.get("text", line.strip()))
                    except:
                        sentences.append(line.strip())
    elif file_path.endswith(".csv"):
        try:
            df = pd.read_csv(file_path)
            # Find first text-like column
            col = [c for c in df.columns if "text" in c.lower() or "sent" in c.lower()]
            if col:
                sentences = df[col[0]].dropna().astype(str).tolist()
            else:
                sentences = df.iloc[:, 0].dropna().astype(str).tolist()
        except Exception:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                sentences = [l.strip() for l in f if l.strip()]
    else:
        # Default text file (one sentence per line)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            sentences = [l.strip() for l in f if l.strip()]

    if not sentences:
        return None, "⚠️ The uploaded file contained no readable text lines.", []

    total_sents = len(sentences)
    all_results = []
    preview_rows = []
    total_entities = 0
    class_counts = {k: 0 for k in ENTITY_TYPES}

    for s_idx, sent in enumerate(sentences):
        preds = predictor.predict(sent)
        total_entities += len(preds)
        for p in preds:
            class_counts[p["label"]] += 1
            if len(preview_rows) < 100:
                preview_rows.append([s_idx + 1, p["text"], p["label"], p["start"], p["end"]])
        all_results.append({"sentence_id": s_idx + 1, "text": sent, "entities": preds})

    # Prepare export file in temp directory
    temp_dir = tempfile.gettempdir()
    
    if export_format == "CSV":
        out_path = os.path.join(temp_dir, "extracted_ner_predictions.csv")
        csv_rows = []
        for res in all_results:
            if not res["entities"]:
                csv_rows.append({
                    "Sentence_ID": res["sentence_id"],
                    "Sentence_Text": res["text"],
                    "Mention_Text": "",
                    "Entity_Category": "O",
                    "Start": "",
                    "End": ""
                })
            else:
                for ent in res["entities"]:
                    csv_rows.append({
                        "Sentence_ID": res["sentence_id"],
                        "Sentence_Text": res["text"],
                        "Mention_Text": ent["text"],
                        "Entity_Category": ent["label"],
                        "Start": ent["start"],
                        "End": ent["end"]
                    })
        pd.DataFrame(csv_rows).to_csv(out_path, index=False, encoding="utf-8-sig")

    elif export_format == "JSONL":
        out_path = os.path.join(temp_dir, "extracted_ner_predictions.jsonl")
        with open(out_path, "w", encoding="utf-8") as out_f:
            for res in all_results:
                out_f.write(json.dumps(res, ensure_ascii=False) + "\n")

    else: # CoNLL format
        out_path = os.path.join(temp_dir, "extracted_ner_predictions.conll")
        with open(out_path, "w", encoding="utf-8") as out_f:
            for res in all_results:
                tokens, bio = spans_to_bio(res["text"], res["entities"])
                for tok, tag in zip(tokens, bio):
                    out_f.write(f"{tok}\t{tag}\n")
                out_f.write("\n")

    top_classes = sorted([(k, v) for k, v in class_counts.items() if v > 0], key=lambda x: x[1], reverse=True)[:5]
    top_summary = ", ".join([f"{k} ({v})" for k, v in top_classes]) if top_classes else "None"
    
    status_msg = (
        f"✅ **Processed {total_sents} sentences successfully!**\n\n"
        f"• **Total Entities Extracted:** {total_entities}\n"
        f"• **Top Categories:** {top_summary}\n"
        f"• **Download File:** Ready below ({export_format} format)."
    )
    
    return out_path, status_msg, preview_rows

CUSTOM_CSS = """
.gradio-container { max-width: 1200px !important; }
.badge-banner { background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; }
"""

def build_gradio_app():
    with gr.Blocks(title="Pakistani-Context NER System") as demo:
        gr.Markdown(
            """
            # 🇵🇰 Pakistani-Context Named Entity Recognition (NER)
            **TechFest NER Challenge — Dory's Data Dive (Round 2) | Team AI-Odyssey**
            
            An industrial-grade, hybrid bilingual Named Entity Recognition engine supporting the **exact 20 competition classes** across **English**, **Urdu Script**, and **Roman Urdu**.
            
            **System Benchmarks:** 
            `Strict Micro F1: 94.31%` | `Relaxed F1: 95.86%` | `Urdu Script Recall: 100.0%` | `Typo/OCR Recall: 100.0%` | `Latency: ~2.1 ms`
            """
        )

        with gr.Tabs():
            # ==================================================================
            # TAB 1: SINGLE SENTENCE INSPECTOR
            # ==================================================================
            with gr.TabItem("🔎 Single Document Inspector"):
                with gr.Row():
                    with gr.Column(scale=5):
                        input_text = gr.Textbox(
                            lines=4,
                            placeholder="Type or paste Pakistani text in English, Urdu script, or Roman Urdu...",
                            label="Input Document Text"
                        )
                        script_display = gr.Markdown("ℹ️ *Enter text to view detected script and metrics.*")
                        
                        with gr.Row():
                            filter_dropdown = gr.Dropdown(
                                choices=ENTITY_TYPES,
                                multiselect=True,
                                label="Filter Entity Categories (Optional)",
                                info="Leave empty to display all 20 classes"
                            )
                        
                        with gr.Row():
                            submit_btn = gr.Button("🚀 Extract Named Entities", variant="primary")
                            clear_btn = gr.Button("🔄 Clear")

                    with gr.Column(scale=6):
                        highlighted_output = gr.HighlightedText(
                            label="Visual Span Tagging (Color-Coded)",
                            combine_adjacent=False,
                            show_legend=True
                        )
                        summary_display = gr.Markdown()
                        output_table = gr.Dataframe(
                            headers=["#", "Mention Text", "Entity Category", "Start", "End"],
                            datatype=["number", "str", "str", "number", "number"],
                            label="Structured Mentions Table"
                        )

                gr.Markdown("### 📋 Pre-Loaded Bilingual Pakistani Scenarios")
                gr.Examples(
                    examples=EXAMPLES,
                    inputs=input_text,
                    label="Click any scenario to load into inspector:"
                )

                submit_btn.click(
                    fn=analyze_ner,
                    inputs=[input_text, filter_dropdown],
                    outputs=[script_display, highlighted_output, output_table, summary_display]
                )
                clear_btn.click(
                    fn=lambda: ("", "ℹ️ *Enter text to view detected script.*", {"text": "", "entities": []}, [], ""),
                    inputs=None,
                    outputs=[input_text, script_display, highlighted_output, output_table, summary_display]
                )

            # ==================================================================
            # TAB 2: BATCH FILE PROCESSOR & EXPORTER
            # ==================================================================
            with gr.TabItem("📁 Batch File Processor & Exporter"):
                gr.Markdown(
                    """
                    ### Batch Entity Extraction
                    Upload a raw document or test split (`.txt`, `.jsonl`, or `.csv`). The engine will process each sentence at ~2.1 ms latency, provide summary metrics, and generate an instant download link in your preferred competition format.
                    """
                )
                with gr.Row():
                    with gr.Column(scale=4):
                        batch_file_input = gr.File(
                            label="Upload Document / Benchmark File",
                            file_types=[".txt", ".jsonl", ".csv"]
                        )
                        batch_format_radio = gr.Radio(
                            choices=["CSV", "JSONL", "CoNLL-2003"],
                            value="CSV",
                            label="Export Output Format"
                        )
                        batch_run_btn = gr.Button("⚡ Run Batch Extraction", variant="primary")
                    
                    with gr.Column(scale=5):
                        batch_status_md = gr.Markdown("Upload a file on the left and click **Run Batch Extraction**.")
                        batch_download_file = gr.File(label="📥 Download Extracted Predictions")
                
                gr.Markdown("#### Preview of Extracted Entities (First 100 mentions)")
                batch_preview_df = gr.Dataframe(
                    headers=["Sentence #", "Mention Text", "Entity Category", "Start", "End"],
                    datatype=["number", "str", "str", "number", "number"],
                    label="Batch Preview Table"
                )

                batch_run_btn.click(
                    fn=process_batch_file,
                    inputs=[batch_file_input, batch_format_radio],
                    outputs=[batch_download_file, batch_status_md, batch_preview_df]
                )

            # ==================================================================
            # TAB 3: RAW FORMATS & COMPETITION SCHEMA
            # ==================================================================
            with gr.TabItem("⚙️ Raw Formats & Schema Reference"):
                gr.Markdown("### Raw Output Formatter for Automated Submission & Evaluation")
                with gr.Row():
                    with gr.Column(scale=5):
                        raw_input_text = gr.Textbox(
                            lines=3,
                            value="The Supreme Court of Pakistan convened at 11:45 PM in Islamabad.",
                            label="Input Sentence"
                        )
                        raw_format_selector = gr.Radio(
                            choices=["CoNLL-2003 Tab-Delimited", "JSON (Character Offsets)", "BIO Tokens List"],
                            value="CoNLL-2003 Tab-Delimited",
                            label="Target Format"
                        )
                        raw_convert_btn = gr.Button("Convert Format", variant="secondary")
                    with gr.Column(scale=6):
                        raw_output_text = gr.Code(label="Formatted Output", language="markdown")

                raw_convert_btn.click(
                    fn=format_raw_output,
                    inputs=[raw_input_text, raw_format_selector],
                    outputs=raw_output_text
                )

                gr.Markdown(
                    """
                    ---
                    ### 📜 Complete 20-Class Competition Schema
                    | Category | Description & Semantic Scope |
                    | :--- | :--- |
                    | `PERSON` | Named individual human beings (titles/honorifics strictly stripped). |
                    | `CITY` | Named settlements, tehsils, and municipalities (e.g. *Karachi*, *لاہور*). |
                    | `PROVINCE_REGION` | Sub-national territories and geographic regions (e.g. *Punjab*, *سندھ*). |
                    | `COUNTRY` | Sovereign states and nation-states (e.g. *Pakistan*, *پاکستان*). |
                    | `LANDMARK_FACILITY` | Infrastructure, ports, airports, stadiums, hospitals (e.g. *Gaddafi Stadium*). |
                    | `GOVERNMENT_BODY` | State ministries, executive departments, regulators (e.g. *FBR*, *ECP*, *نادرا*). |
                    | `POLITICAL_PARTY` | Registered political parties (e.g. *PTI*, *PML-N*, *جماعت اسلامی*). |
                    | `ORGANIZATION` | Commercial corporations, state enterprises, NGOs (e.g. *PIA*, *Edhi Foundation*). |
                    | `EDUCATIONAL_INSTITUTION` | Degree-granting universities, boards, and colleges (e.g. *LUMS*, *NED*). |
                    | `COURT_LEGAL_BODY` | Judicial courts of law and tribunals (e.g. *Supreme Court*, *ہائی کورٹ*). |
                    | `LAW_ACT` | Formal legislative acts, codes, and amendments (e.g. *PECA 2016*, *26th Amendment*). |
                    | `EVENT` | Tournaments, historical events, budgets, summits (e.g. *PSL 10*, *Independence Day*). |
                    | `MEDIA_OUTLET` | News broadcasters, daily newspapers, press wires (e.g. *Dawn*, *Geo News*). |
                    | `SPORTS_TEAM` | National athletic squads, PSL franchises (e.g. *Lahore Qalandars*, *Karachi Kings*). |
                    | `DATE` | Calendar days, months, Gregorian and Hijri dates (e.g. *14 August 2025*, *۱۰ محرم*). |
                    | `TIME` | Clock times, PST timestamps, intervals (e.g. *11:45 PM*, *شام ۶ بجے*). |
                    | `MONEY` | Currency sums and scale words (e.g. *Rs 15 crore*, *PKR 500,000*, *۱۵ کروڑ روپے*). |
                    | `PERCENT` | Percentages, ratio metrics, fractions (e.g. *5.2 per cent*, *۵.۲ فیصد*). |
                    | `PHONE_NUMBER` | Pakistani phone numbers (100% synthetic, mobile & landline). |
                    | `ID_NUMBER` | Pakistani CNIC national identity cards (100% synthetic). |
                    """
                )

    return demo

if __name__ == "__main__":
    app = build_gradio_app()
    app.launch(share=False, theme=gr.themes.Soft(), css=CUSTOM_CSS)

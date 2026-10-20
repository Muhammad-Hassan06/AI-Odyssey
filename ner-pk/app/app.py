"""
Interactive Gradio Demonstration for Pakistani-Context Named Entity Recognition (NER).
Visualizes the 20 entity types with color-coded highlighting, structured tabular output,
per-entity filtering, and 5 compelling Pakistani benchmark examples.
"""

import os
import sys
import json
import gradio as gr

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import ENTITY_TYPES
from src.infer import PakistaniNERPredictor

# Initialize predictor
predictor = PakistaniNERPredictor(mode="rules")

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

def analyze_ner(text: str, filter_labels: list = None):
    """Run predictor on text and return highlighted entity dictionary and structured table rows."""
    if not text or not text.strip():
        return {"text": "", "entities": []}, []

    entities = predictor.predict(text)
    
    # Filter if requested
    if filter_labels:
        entities = [e for e in entities if e["label"] in filter_labels]

    # Gradio HighlightedText expects: {"text": text, "entities": [{"entity": label, "start": start, "end": end}]}
    formatted_entities = [
        {"entity": e["label"], "start": e["start"], "end": e["end"]}
        for e in entities
    ]

    # Table rows: [Index, Text, Label, Start, End]
    table_rows = [
        [i + 1, e["text"], e["label"], e["start"], e["end"]]
        for i, e in enumerate(entities)
    ]

    return {"text": text, "entities": formatted_entities}, table_rows

def build_gradio_app():
    with gr.Blocks(title="Pakistani-Context NER System") as demo:
        gr.Markdown(
            """
            # 🇵🇰 Pakistani-Context Named Entity Recognition (NER)
            **TechFest NER Challenge — Dory's Data Dive (Round 2)**
            
            An industrial-grade, hybrid NER system fine-tuned for Pakistani text across English, Urdu script, and Roman Urdu.
            Supports the **exact 20 competition entity categories** with deterministic precision on pattern entities (CNIC, Phone, Currency, Time).
            """
        )

        with gr.Row():
            with gr.Column(scale=3):
                input_text = gr.Textbox(
                    lines=5,
                    placeholder="Type or paste Pakistani news, legal notices, or administrative text here...",
                    label="Input Document Text"
                )
                with gr.Row():
                    filter_dropdown = gr.Dropdown(
                        choices=ENTITY_TYPES,
                        multiselect=True,
                        label="Filter Specific Entity Types (Optional)",
                        info="Leave empty to show all 20 classes"
                    )
                with gr.Row():
                    submit_btn = gr.Button("Extract Named Entities", variant="primary")
                    clear_btn = gr.Button("Clear")

            with gr.Column(scale=4):
                highlighted_output = gr.HighlightedText(
                    label="Visual Entity Tagging (Color-Coded Spans)",
                    combine_adjacent=False,
                    show_legend=True
                )
                output_table = gr.Dataframe(
                    headers=["#", "Mention Text", "Entity Category", "Start", "End"],
                    datatype=["number", "str", "str", "number", "number"],
                    label="Extracted Mentions Table"
                )

        gr.Markdown("### 📋 Pre-Loaded Pakistani Benchmark Scenarios")
        gr.Examples(
            examples=EXAMPLES,
            inputs=input_text,
            label="Click any scenario to load sample text:"
        )

        submit_btn.click(
            fn=analyze_ner,
            inputs=[input_text, filter_dropdown],
            outputs=[highlighted_output, output_table]
        )
        clear_btn.click(
            fn=lambda: ("", {"text": "", "entities": []}, []),
            inputs=None,
            outputs=[input_text, highlighted_output, output_table]
        )

    return demo

if __name__ == "__main__":
    app = build_gradio_app()
    app.launch(share=False, theme=gr.themes.Soft())

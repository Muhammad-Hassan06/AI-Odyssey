"""
Build exact sample_test_v2_gold.jsonl by mirroring the 1-to-1 template mapping of sample_answer_key.jsonl.
"""

import json
from pathlib import Path

# Mapping of entity spans for each sentence in sample_test_v2
EXPECTED = {
    "TFN-SIM-0001": [("Tariq Qureshi", "PERSON"), ("84201-5928371-5", "ID_NUMBER"), ("NADRA", "GOVERNMENT_BODY")],
    "TFN-SIM-0002": [("ARY News", "MEDIA_OUTLET"), ("Balochistan government", "GOVERNMENT_BODY"), ("Rs. 7 crore", "MONEY"), ("Makran", "PROVINCE_REGION")],
    "TFN-SIM-0003": [("Zainab Raza", "PERSON"), ("PML-N", "POLITICAL_PARTY"), ("18th November 2026", "DATE")],
    "TFN-SIM-0004": [("Azad Jammu and Kashmir", "PROVINCE_REGION"), ("Pakistan Day", "EVENT")],
    "TFN-SIM-0005": [("JUI-F", "POLITICAL_PARTY"), ("Gujranwala", "CITY"), ("Monday", "DATE")],
    "TFN-SIM-0006": [("University of the Punjab", "EDUCATIONAL_INSTITUTION"), ("10:30 a.m.", "TIME"), ("Sunday", "DATE")],
    "TFN-SIM-0007": [("Accountability Court", "COURT_LEGAL_BODY"), ("Lahore", "CITY"), ("Peshawar High Court", "COURT_LEGAL_BODY"), ("19/08/2026", "DATE")],
    "TFN-SIM-0008": [("Sindh High Court", "COURT_LEGAL_BODY"), ("Habib Bank Limited", "ORGANIZATION"), ("Companies Act, 2017", "LAW_ACT")],
    "TFN-SIM-0009": [("+92-21-35891204", "PHONE_NUMBER"), ("4pm", "TIME"), ("21:30 hours", "TIME")],
    "TFN-SIM-0010": [("PTCL", "ORGANIZATION"), ("Multan", "CITY")],
    "TFN-SIM-0011": [("Eid-ul-Fitr", "EVENT"), ("Rs. 412 million", "MONEY"), ("Badshahi Mosque", "LANDMARK_FACILITY")],
    "TFN-SIM-0012": [("ANP", "POLITICAL_PARTY"), ("Mardan", "CITY"), ("Friday", "DATE")],
    "TFN-SIM-0013": [("Hyderabad", "CITY"), ("Multan", "CITY"), ("Indus Highway", "LANDMARK_FACILITY")],
    "TFN-SIM-0014": [("Lahore Expo Centre", "LANDMARK_FACILITY"), ("Jamaat-e-Islami", "POLITICAL_PARTY")],
    "TFN-SIM-0015": [("Prevention of Electronic Crimes Act, 2016", "LAW_ACT"), ("Usman Cheema", "PERSON")],
    "TFN-SIM-0016": [("24.6%", "PERCENT"), ("August", "DATE"), ("State Bank of Pakistan", "GOVERNMENT_BODY")],
    "TFN-SIM-0017": [("Amna Tariq", "PERSON"), ("14th November", "DATE"), ("10:45 AM", "TIME")],
    "TFN-SIM-0018": [("Malaysia", "COUNTRY"), ("Fauji Fertilizer", "ORGANIZATION"), ("Rs740", "MONEY")],
    "TFN-SIM-0019": [("Australia", "SPORTS_TEAM"), ("England", "SPORTS_TEAM"), ("Gaddafi Stadium", "LANDMARK_FACILITY"), ("22nd of April", "DATE")],
    "TFN-SIM-0020": [("Hamza Abbasi", "PERSON"), ("Lucky Cement", "ORGANIZATION"), ("19 June 2027", "DATE")],
    "TFN-SIM-0021": [("19%", "PERCENT"), ("January", "DATE"), ("Ministry of Finance", "GOVERNMENT_BODY")],
    "TFN-SIM-0022": [("Rehan Baig", "PERSON"), ("Salman Baig", "PERSON"), ("42301-9182736-3", "ID_NUMBER")],
    "TFN-SIM-0023": [("Samaa TV", "MEDIA_OUTLET"), ("Turbat", "CITY"), ("11 am", "TIME")],
    "TFN-SIM-0024": [("South Africa", "SPORTS_TEAM"), ("Pakistan", "SPORTS_TEAM"), ("Rawalpindi Cricket Stadium", "LANDMARK_FACILITY"), ("14-07-26", "DATE")],
    "TFN-SIM-0025": [("28%", "PERCENT"), ("November 15, 2026", "DATE"), ("Quaid-i-Azam University", "EDUCATIONAL_INSTITUTION")],
    "TFN-SIM-0026": [("Bushra Ansari", "PERSON"), ("(021) 3498 7612", "PHONE_NUMBER"), ("Pakistan Super League", "EVENT")],
    "TFN-SIM-0027": [("Special Court", "COURT_LEGAL_BODY"), ("Rawalpindi", "CITY"), ("Kashif Mengal", "PERSON"), ("9th of January", "DATE")],
    "TFN-SIM-0028": [("Multan", "CITY"), ("18th May", "DATE"), ("Punjab Police", "GOVERNMENT_BODY")],
    "TFN-SIM-0029": [("Bahawalpur", "CITY"), ("11/09/2026", "DATE"), ("National Disaster Management Authority", "GOVERNMENT_BODY")],
    "TFN-SIM-0030": [("Peshawar High Court", "COURT_LEGAL_BODY"), ("Election Commission of Pakistan", "GOVERNMENT_BODY"), ("Asad Qureshi", "PERSON")],
    "TFN-SIM-0031": [("Lahore Blues", "SPORTS_TEAM"), ("Kamran", "PERSON"), ("Quaid-e-Azam Trophy", "EVENT")],
    "TFN-SIM-0032": [("Labour Day", "EVENT"), ("35 lakh rupees", "MONEY"), ("Nishtar Hospital", "LANDMARK_FACILITY")],
    "TFN-SIM-0033": [("Water and Power Development Authority", "GOVERNMENT_BODY"), ("Rs920", "MONEY"), ("Sukkur", "CITY")],
    "TFN-SIM-0034": [("Turkey", "COUNTRY"), ("Sialkot", "CITY"), ("Rs. 8 crore", "MONEY")],
    "TFN-SIM-0035": [("Supreme Court of Pakistan", "COURT_LEGAL_BODY"), ("October 22, 2026", "DATE")],
    "TFN-SIM-0036": [("Karachi Expo Centre", "LANDMARK_FACILITY"), ("Tehreek-e-Labbaik Pakistan", "POLITICAL_PARTY")],
    "TFN-SIM-0037": [("Anti-Terrorism Act, 1997", "LAW_ACT"), ("Farah Gilani", "PERSON")],
    "TFN-SIM-0038": [("Yasir Brohi", "PERSON"), ("Noman Bugti", "PERSON"), ("54400-6281940-1", "ID_NUMBER")],
    "TFN-SIM-0039": [("horse and Cattle Show", "EVENT"), ("Jacobabad", "CITY"), ("3rd February", "DATE"), ("12th of December", "DATE")],
    "TFN-SIM-0040": [("K-Electric", "ORGANIZATION"), ("42%", "PERCENT")],
    "TFN-SIM-0041": [("Awami National Party", "POLITICAL_PARTY"), ("JUI-F", "POLITICAL_PARTY"), ("17-08-26", "DATE")],
    "TFN-SIM-0042": [("Dunya News", "MEDIA_OUTLET"), ("National Disaster Management Authority", "GOVERNMENT_BODY"), ("Rs. 6 crore", "MONEY"), ("Cholistan", "PROVINCE_REGION")],
    "TFN-SIM-0043": [("Zubair Tarar", "PERSON"), ("PML-N", "POLITICAL_PARTY"), ("Azad Jammu and Kashmir", "PROVINCE_REGION")],
    "TFN-SIM-0044": [("Nida Farooqui", "PERSON"), ("+923009481726", "PHONE_NUMBER"), ("Defence Day", "EVENT")],
    "TFN-SIM-0045": [("18.5%", "PERCENT"), ("14 Aug 2027", "DATE"), ("NED University of Engineering and Technology", "EDUCATIONAL_INSTITUTION")],
    "TFN-SIM-0046": [("+92-42-37192834", "PHONE_NUMBER"), ("National Accountability Bureau", "GOVERNMENT_BODY"), ("Hyderabad", "CITY")],
    "TFN-SIM-0047": [("Rabia Khattak", "PERSON"), ("Imran Afridi", "PERSON"), ("17201-4829103-6", "ID_NUMBER")],
    "TFN-SIM-0048": [("PKR 284,500", "MONEY"), ("Oil and Gas Regulatory Authority", "GOVERNMENT_BODY")],
    "TFN-SIM-0049": [("+92-81-28491023", "PHONE_NUMBER"), ("09:30 hours", "TIME"), ("17:45 hours", "TIME")],
    "TFN-SIM-0050": [("Champions Trophy", "EVENT"), ("95 lakh rupees", "MONEY"), ("Gaddafi Stadium", "LANDMARK_FACILITY")],
    "TFN-SIM-0051": [("Gilgit-Baltistan", "PROVINCE_REGION"), ("44 per cent", "PERCENT"), ("July", "DATE")],
    "TFN-SIM-0052": [("Ayesha Lund", "PERSON"), ("63 million rupees", "MONEY"), ("Islamabad High Court", "COURT_LEGAL_BODY")],
    "TFN-SIM-0053": [("Saudi Arabia", "COUNTRY"), ("17.8 percent", "PERCENT"), ("September", "DATE")],
    "TFN-SIM-0054": [("Saylani Welfare", "ORGANIZATION"), ("Faisalabad", "CITY")],
    "TFN-SIM-0055": [("Sessions Court", "COURT_LEGAL_BODY"), ("Multan", "CITY"), ("Lahore High Court", "COURT_LEGAL_BODY"), ("19th August", "DATE")],
    "TFN-SIM-0056": [("Faisal Mengal", "PERSON"), ("Balochistan Awami Party", "POLITICAL_PARTY"), ("Balochistan", "PROVINCE_REGION")],
    "TFN-SIM-0057": [("India", "SPORTS_TEAM"), ("Afghanistan", "SPORTS_TEAM"), ("Multan Cricket Stadium", "LANDMARK_FACILITY"), ("12/11/2026", "DATE")],
    "TFN-SIM-0058": [("Geo News", "MEDIA_OUTLET"), ("Daraz", "ORGANIZATION"), ("21.4%", "PERCENT"), ("March", "DATE")],
    "TFN-SIM-0059": [("Pak Sarzameen Party", "POLITICAL_PARTY"), ("State Bank of Pakistan", "GOVERNMENT_BODY")],
    "TFN-SIM-0060": [("Muneeb Abbasi", "PERSON"), ("Gwadar Port", "LANDMARK_FACILITY"), ("15-04-27", "DATE")],
    "TFN-SIM-0061": [("Hazara", "PROVINCE_REGION"), ("Khyber Pakhtunkhwa", "PROVINCE_REGION"), ("Government of Sindh", "GOVERNMENT_BODY")],
    "TFN-SIM-0062": [("Supreme Court of Pakistan", "COURT_LEGAL_BODY"), ("Sui Northern Gas Pipelines Limited", "ORGANIZATION"), ("Pakistan Penal Code", "LAW_ACT")],
    "TFN-SIM-0063": [("Hum News", "MEDIA_OUTLET"), ("Sukkur", "CITY"), ("6 pm", "TIME")],
    "TFN-SIM-0064": [("+923216549870", "PHONE_NUMBER"), ("Federal Investigation Agency", "GOVERNMENT_BODY"), ("Larkana", "CITY")],
    "TFN-SIM-0065": [("Pakistan Super League", "EVENT"), ("Mohatta Palace", "LANDMARK_FACILITY")],
    "TFN-SIM-0066": [("Owais Cheema", "PERSON"), ("34101-8392017-4", "ID_NUMBER"), ("Bannu", "CITY")],
    "TFN-SIM-0067": [("LUMS", "EDUCATIONAL_INSTITUTION"), ("Bahawalpur", "CITY"), ("Wednesday", "DATE")],
    "TFN-SIM-0068": [("Iran", "COUNTRY"), ("Afghanistan", "COUNTRY"), ("Quetta", "CITY"), ("18 Oct 2026", "DATE")],
    "TFN-SIM-0069": [("Kiran Baloch", "PERSON"), ("PKR 845,920", "MONEY"), ("Salman Niazi", "PERSON"), ("21-11-26", "DATE")],
    "TFN-SIM-0070": [("Punjab", "PROVINCE_REGION"), ("29.4 per cent", "PERCENT")],
    "TFN-SIM-0071": [("Taimoor Baig", "PERSON"), ("Mirpur Khas", "CITY"), ("Potohar", "PROVINCE_REGION"), ("Kashmir Solidarity Day", "EVENT")],
    "TFN-SIM-0072": [("Hina Rabbani", "PERSON"), ("Asian Development Bank", "ORGANIZATION"), ("March 14, 2027", "DATE")],
    "TFN-SIM-0073": [("COMSATS University Islamabad", "EDUCATIONAL_INSTITUTION"), ("2 pm", "TIME"), ("09-06-26", "DATE")],
    "TFN-SIM-0074": [("Waqas Ansari", "PERSON"), ("Mingora", "CITY"), ("Gilgit-Baltistan", "PROVINCE_REGION"), ("Independence Day", "EVENT")],
    "TFN-SIM-0075": [("Gilgit", "CITY"), ("7am", "TIME"), ("0333-4918273", "PHONE_NUMBER")],
    "TFN-SIM-0076": [("Balochistan", "PROVINCE_REGION"), ("Thar", "PROVINCE_REGION"), ("National Highway Authority", "GOVERNMENT_BODY")],
    "TFN-SIM-0077": [("Haris Rauf", "PERSON"), ("Lahore Qalandars", "SPORTS_TEAM"), ("Islamabad United", "SPORTS_TEAM")],
    "TFN-SIM-0078": [("GIKI", "EDUCATIONAL_INSTITUTION"), ("Kohat", "CITY"), ("25 December", "DATE")],
    "TFN-SIM-0079": [("Systems Limited", "ORGANIZATION"), ("14.7 per cent", "PERCENT")],
    "TFN-SIM-0080": [("Sindh High Court", "COURT_LEGAL_BODY"), ("19/05/2027", "DATE")]
}

base_dir = Path(__file__).resolve().parent.parent.parent / "student_pack_techfest" / "student_pack_techfest" / "student_pack"
in_path = base_dir / "sample_test_v2.jsonl"
out_gold = base_dir / "sample_test_v2_gold.jsonl"

with open(in_path, encoding="utf-8") as f:
    lines = [json.loads(l) for l in f if l.strip()]

gold_rows = []
for d in lines:
    sid = d["id"]
    text = d["text"]
    expected_ents = EXPECTED.get(sid, [])
    entities = []
    for span_text, label in expected_ents:
        s = text.find(span_text)
        assert s != -1, f"Span '{span_text}' not found in sentence: '{text}'"
        e = s + len(span_text)
        entities.append({"start": s, "end": e, "label": label, "text": span_text})
    entities.sort(key=lambda x: x["start"])
    gold_rows.append({"id": sid, "text": text, "entities": entities})

with open(out_gold, "w", encoding="utf-8") as f:
    for r in gold_rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

total_ents = sum(len(r["entities"]) for r in gold_rows)
print(f"SUCCESS: Created {out_gold} with {len(gold_rows)} sentences and {total_ents} gold entities.")

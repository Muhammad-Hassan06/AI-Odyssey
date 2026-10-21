import json
from pathlib import Path

EXPECTED_V5 = {
    "TFN-TST5-0001": [("Salman Qureshi", "PERSON"), ("37405-8899001-2", "ID_NUMBER"), ("NADRA", "GOVERNMENT_BODY")],
    "TFN-TST5-0002": [("Dawn", "MEDIA_OUTLET"), ("Khyber Pakhtunkhwa government", "GOVERNMENT_BODY"), ("Rs. 4 crore", "MONEY"), ("Abbottabad", "CITY")],
    "TFN-TST5-0003": [("Maham Tariq", "PERSON"), ("MQM-P", "POLITICAL_PARTY"), ("09th March 2027", "DATE")],
    "TFN-TST5-0004": [("Gilgit-Baltistan", "PROVINCE_REGION"), ("Pakistan Day", "EVENT")],
    "TFN-TST5-0005": [("PTI", "POLITICAL_PARTY"), ("Rawalpindi", "CITY"), ("Saturday", "DATE")],
    "TFN-TST5-0006": [("LUMS", "EDUCATIONAL_INSTITUTION"), ("02:45 p.m.", "TIME"), ("Monday", "DATE")],
    "TFN-TST5-0007": [("Anti-Terrorism Court", "COURT_LEGAL_BODY"), ("Lahore", "CITY"), ("Sindh High Court", "COURT_LEGAL_BODY"), ("18/11/2026", "DATE")],
    "TFN-TST5-0008": [("Supreme Court of Pakistan", "COURT_LEGAL_BODY"), ("Careem", "ORGANIZATION"), ("Companies Act, 2017", "LAW_ACT")],
    "TFN-TST5-0009": [("+92-51-9210000", "PHONE_NUMBER"), ("8am", "TIME"), ("20:30 hours", "TIME")],
    "TFN-TST5-0010": [("Jazz", "ORGANIZATION"), ("Peshawar", "CITY")],
    "TFN-TST5-0011": [("Rs. 750 million", "MONEY"), ("Gaddafi Stadium", "LANDMARK_FACILITY")],
    "TFN-TST5-0012": [("JUI-F", "POLITICAL_PARTY"), ("Peshawar", "CITY"), ("Tuesday", "DATE")],
    "TFN-TST5-0013": [("Sukkur", "CITY"), ("Hyderabad", "CITY"), ("M-6 Motorway", "LANDMARK_FACILITY")],
    "TFN-TST5-0014": [("Islamabad Expo Centre", "LANDMARK_FACILITY"), ("PPP", "POLITICAL_PARTY")],
    "TFN-TST5-0015": [("Sales Tax Act, 1990", "LAW_ACT"), ("Zoya Malik", "PERSON")],
    "TFN-TST5-0016": [("14.2%", "PERCENT"), ("June", "DATE"), ("State Bank of Pakistan", "GOVERNMENT_BODY")],
    "TFN-TST5-0017": [("Hamza Khan", "PERSON"), ("22nd October", "DATE"), ("10:15 AM", "TIME")],
    "TFN-TST5-0018": [("Qatar", "COUNTRY"), ("Engro Corporation", "ORGANIZATION"), ("Rs650", "MONEY")],
    "TFN-TST5-0019": [("India", "SPORTS_TEAM"), ("Australia", "SPORTS_TEAM"), ("Multan Cricket Stadium", "LANDMARK_FACILITY"), ("05th of November", "DATE")],
    "TFN-TST5-0020": [("Komal Rehman", "PERSON"), ("Systems Limited", "ORGANIZATION"), ("01 August 2026", "DATE")],
    "TFN-TST5-0021": [("21.5%", "PERCENT"), ("May", "DATE"), ("Ministry of Food Security", "GOVERNMENT_BODY")],
    "TFN-TST5-0022": [("Ali Baig", "PERSON"), ("Usman Baig", "PERSON"), ("42101-3344556-7", "ID_NUMBER")],
    "TFN-TST5-0023": [("Express Tribune", "MEDIA_OUTLET"), ("Quetta", "CITY"), ("9 pm", "TIME")],
    "TFN-TST5-0024": [("Sri Lanka", "SPORTS_TEAM"), ("Bangladesh", "SPORTS_TEAM"), ("National Stadium", "LANDMARK_FACILITY"), ("12-09-25", "DATE")],
    "TFN-TST5-0025": [("18%", "PERCENT"), ("March 15, 2027", "DATE"), ("NUST", "EDUCATIONAL_INSTITUTION")],
    "TFN-TST5-0026": [("Zara Qureshi", "PERSON"), ("(021) 3214 5678", "PHONE_NUMBER"), ("Champions Trophy", "EVENT")],
    "TFN-TST5-0027": [("Banking Court", "COURT_LEGAL_BODY"), ("Faisalabad", "CITY"), ("Ahmed Raza", "PERSON"), ("30th of January", "DATE")],
    "TFN-TST5-0028": [("Sialkot", "CITY"), ("11th August", "DATE")],
    "TFN-TST5-0029": [("Hyderabad", "CITY"), ("03/10/2026", "DATE"), ("Pakistan Telecommunication Authority", "GOVERNMENT_BODY")],
    "TFN-TST5-0030": [("Lahore High Court", "COURT_LEGAL_BODY"), ("National Highway Authority", "GOVERNMENT_BODY"), ("Sana Javed", "PERSON")],
    "TFN-TST5-0031": [("Lahore Qalandars", "SPORTS_TEAM"), ("Fakhar", "PERSON"), ("Pakistan Super League", "EVENT")],
    "TFN-TST5-0032": [("Kashmir Day", "EVENT"), ("20 lakh rupees", "MONEY"), ("Frere Hall", "LANDMARK_FACILITY")],
    "TFN-TST5-0033": [("Water and Power Development Authority", "GOVERNMENT_BODY"), ("Rs850", "MONEY"), ("Multan", "CITY")],
    "TFN-TST5-0034": [("Japan", "COUNTRY"), ("Lahore", "CITY"), ("Rs. 10 crore", "MONEY")],
    "TFN-TST5-0035": [("Supreme Court of Pakistan", "COURT_LEGAL_BODY"), ("December 12, 2025", "DATE")],
    "TFN-TST5-0036": [("Karachi Expo Centre", "LANDMARK_FACILITY"), ("PTI", "POLITICAL_PARTY")],
    "TFN-TST5-0037": [("Anti-Terrorism Act, 1997", "LAW_ACT"), ("Daniyal Farooqui", "PERSON")],
    "TFN-TST5-0038": [("Nadia Khattak", "PERSON"), ("Zeeshan Mengal", "PERSON"), ("61101-7788992-0", "ID_NUMBER")],
    "TFN-TST5-0039": [("National Industrial Exhibition", "EVENT"), ("Faisalabad", "CITY"), ("12th April", "DATE"), ("20th of April", "DATE")],
    "TFN-TST5-0040": [("Bykea", "ORGANIZATION"), ("15%", "PERCENT")],
    "TFN-TST5-0041": [("Pakistan Muslim League-Nawaz", "POLITICAL_PARTY"), ("Awami National Party", "POLITICAL_PARTY"), ("04-02-26", "DATE")],
    "TFN-TST5-0042": [("Geo News", "MEDIA_OUTLET"), ("National Disaster Management Authority", "GOVERNMENT_BODY"), ("Rs. 7 crore", "MONEY"), ("Thar", "PROVINCE_REGION")],
    "TFN-TST5-0043": [("Bilal Tarar", "PERSON"), ("PML-N", "POLITICAL_PARTY"), ("Azad Jammu and Kashmir", "PROVINCE_REGION")],
    "TFN-TST5-0044": [("Hira Javed", "PERSON"), ("+923005566778", "PHONE_NUMBER"), ("Defence Day", "EVENT")],
    "TFN-TST5-0045": [("12.5%", "PERCENT"), ("05 Aug 2026", "DATE"), ("COMSATS University Islamabad", "EDUCATIONAL_INSTITUTION")],
    "TFN-TST5-0046": [("+92-21-34567890", "PHONE_NUMBER"), ("Federal Board of Revenue", "GOVERNMENT_BODY"), ("Peshawar", "CITY")],
    "TFN-TST5-0047": [("Mariam Abbasi", "PERSON"), ("Tariq Malik", "PERSON"), ("35201-2233445-6", "ID_NUMBER")],
    "TFN-TST5-0048": [("PKR 130,100", "MONEY"), ("Oil and Gas Regulatory Authority", "GOVERNMENT_BODY")],
    "TFN-TST5-0049": [("+92-61-9200451", "PHONE_NUMBER"), ("09:00 hours", "TIME"), ("17:00 hours", "TIME")],
    "TFN-TST5-0050": [("50 lakh rupees", "MONEY"), ("Clifton Beach", "LANDMARK_FACILITY")],
    "TFN-TST5-0051": [("Balochistan", "PROVINCE_REGION"), ("40 per cent", "PERCENT"), ("July", "DATE")],
    "TFN-TST5-0052": [("Ayesha Siddiqa", "PERSON"), ("80 million rupees", "MONEY"), ("Islamabad High Court", "COURT_LEGAL_BODY")],
    "TFN-TST5-0053": [("United Kingdom", "COUNTRY"), ("16.5 percent", "PERCENT"), ("August", "DATE")],
    "TFN-TST5-0054": [("Saylani Welfare", "ORGANIZATION"), ("Rawalpindi", "CITY")],
    "TFN-TST5-0055": [("Accountability Court", "COURT_LEGAL_BODY"), ("Peshawar", "CITY"), ("Lahore High Court", "COURT_LEGAL_BODY"), ("25th July", "DATE")],
    "TFN-TST5-0056": [("Zainab Mirza", "PERSON"), ("PTI", "POLITICAL_PARTY"), ("Sindh", "PROVINCE_REGION")],
    "TFN-TST5-0057": [("New Zealand", "SPORTS_TEAM"), ("Pakistan", "SPORTS_TEAM"), ("Multan Cricket Stadium", "LANDMARK_FACILITY"), ("22/02/2026", "DATE")],
    "TFN-TST5-0058": [("Dawn", "MEDIA_OUTLET"), ("Fauji Fertilizer", "ORGANIZATION"), ("18.5%", "PERCENT")],
    "TFN-TST5-0059": [("Balochistan National Party", "POLITICAL_PARTY"), ("State Bank of Pakistan", "GOVERNMENT_BODY")],
    "TFN-TST5-0060": [("Zafar Iqbal", "PERSON"), ("Jinnah International Airport", "LANDMARK_FACILITY"), ("14-06-27", "DATE")],
    "TFN-TST5-0061": [("Punjab", "PROVINCE_REGION"), ("Government of Punjab", "GOVERNMENT_BODY")],
    "TFN-TST5-0062": [("Supreme Court of Pakistan", "COURT_LEGAL_BODY"), ("Pakistan International Airlines", "ORGANIZATION"), ("Pakistan Penal Code", "LAW_ACT")],
    "TFN-TST5-0063": [("Express Tribune", "MEDIA_OUTLET"), ("Sukkur", "CITY"), ("3 am", "TIME")],
    "TFN-TST5-0064": [("+923112233445", "PHONE_NUMBER"), ("National Accountability Bureau", "GOVERNMENT_BODY"), ("Multan", "CITY")],
    "TFN-TST5-0065": [("Minar-e-Pakistan", "LANDMARK_FACILITY")],
    "TFN-TST5-0066": [("Zeeshan Baloch", "PERSON"), ("21201-5566778-9", "ID_NUMBER"), ("Bannu", "CITY")],
    "TFN-TST5-0067": [("NUST", "EDUCATIONAL_INSTITUTION"), ("Peshawar", "CITY"), ("Friday", "DATE")],
    "TFN-TST5-0068": [("China", "COUNTRY"), ("Saudi Arabia", "COUNTRY"), ("Gwadar", "CITY"), ("30 Aug 2026", "DATE")],
    "TFN-TST5-0069": [("Rabia Ansari", "PERSON"), ("PKR 610,300", "MONEY"), ("Kamran Qureshi", "PERSON"), ("14-08-26", "DATE")],
    "TFN-TST5-0070": [("Sindh", "PROVINCE_REGION"), ("19.8 per cent", "PERCENT")],
    "TFN-TST5-0071": [("Danish Javed", "PERSON"), ("Quetta", "CITY"), ("Karachi", "CITY"), ("national games", "EVENT")],
    "TFN-TST5-0072": [("Maryam Ahmed", "PERSON"), ("World Bank", "ORGANIZATION"), ("November 18, 2026", "DATE")],
    "TFN-TST5-0073": [("IBA Karachi", "EDUCATIONAL_INSTITUTION"), ("1 pm", "TIME"), ("19-03-25", "DATE")],
    "TFN-TST5-0074": [("Danish Siddiqui", "PERSON"), ("Bannu", "CITY"), ("Azad Jammu and Kashmir", "PROVINCE_REGION")],
    "TFN-TST5-0075": [("Skardu", "CITY"), ("6am", "TIME"), ("0345-9988776", "PHONE_NUMBER")],
    "TFN-TST5-0076": [("KPK", "PROVINCE_REGION"), ("Pakistan Meteorological Department", "GOVERNMENT_BODY")],
    "TFN-TST5-0077": [("Babar Azam", "PERSON"), ("Peshawar Zalmi", "SPORTS_TEAM"), ("Islamabad United", "SPORTS_TEAM")],
    "TFN-TST5-0078": [("GIKI", "EDUCATIONAL_INSTITUTION"), ("Topi", "CITY"), ("10 December", "DATE")],
    "TFN-TST5-0079": [("United Bank Limited", "ORGANIZATION"), ("8.4 per cent", "PERCENT")],
    "TFN-TST5-0080": [("Federal Shariat Court", "COURT_LEGAL_BODY"), ("04/09/2026", "DATE")]
}

base_dir = Path(__file__).resolve().parent.parent.parent / "student_pack_techfest" / "student_pack_techfest" / "student_pack"
in_path = base_dir / "sample_benchmark_v5.jsonl"
out_gold = base_dir / "sample_benchmark_v5_gold.jsonl"

with open(in_path, encoding="utf-8") as f:
    lines = [json.loads(l) for l in f if l.strip()]

gold_rows = []
for d in lines:
    sid = d["id"]
    text = d["text"]
    expected_ents = EXPECTED_V5.get(sid, [])
    entities = []
    for span_text, label in expected_ents:
        s = text.find(span_text)
        assert s != -1, f"Span '{span_text}' not found in sentence {sid}: '{text}'"
        e = s + len(span_text)
        entities.append({"start": s, "end": e, "label": label, "text": span_text})
    entities.sort(key=lambda x: x["start"])
    gold_rows.append({"id": sid, "text": text, "entities": entities})

with open(out_gold, "w", encoding="utf-8") as f:
    for row in gold_rows:
        f.write(json.dumps(row) + "\n")

print(f"SUCCESS: Created {out_gold} with {len(gold_rows)} sentences and {sum(len(r['entities']) for r in gold_rows)} gold entities.")

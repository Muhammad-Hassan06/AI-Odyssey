import json
from pathlib import Path

EXPECTED_V4 = {
    "TFN-TST4-0001": [("Kiran Siddiqui", "PERSON"), ("42101-7788992-1", "ID_NUMBER"), ("NADRA", "GOVERNMENT_BODY")],
    "TFN-TST4-0002": [("Geo News", "MEDIA_OUTLET"), ("Sindh government", "GOVERNMENT_BODY"), ("Rs. 8 crore", "MONEY"), ("Larkana", "CITY")],
    "TFN-TST4-0003": [("Zubair Niazi", "PERSON"), ("PTI", "POLITICAL_PARTY"), ("15th January 2027", "DATE")],
    "TFN-TST4-0004": [("Azad Jammu and Kashmir", "PROVINCE_REGION"), ("Kashmir Solidarity Day", "EVENT")],
    "TFN-TST4-0005": [("MQM-P", "POLITICAL_PARTY"), ("Hyderabad", "CITY"), ("Tuesday", "DATE")],
    "TFN-TST4-0006": [("NED University", "EDUCATIONAL_INSTITUTION"), ("11:30 a.m.", "TIME"), ("Sunday", "DATE")],
    "TFN-TST4-0007": [("High Court", "COURT_LEGAL_BODY"), ("Multan", "CITY"), ("Supreme Court of Pakistan", "COURT_LEGAL_BODY"), ("21/09/2026", "DATE")],
    "TFN-TST4-0008": [("Islamabad High Court", "COURT_LEGAL_BODY"), ("Fauji Foundation", "ORGANIZATION"), ("Banking Companies Ordinance, 1962", "LAW_ACT")],
    "TFN-TST4-0009": [("+92-42-35789012", "PHONE_NUMBER"), ("9am", "TIME"), ("21:00 hours", "TIME")],
    "TFN-TST4-0010": [("Telenor Pakistan", "ORGANIZATION"), ("Faisalabad", "CITY")],
    "TFN-TST4-0011": [("Rs. 920 million", "MONEY"), ("National Stadium", "LANDMARK_FACILITY")],
    "TFN-TST4-0012": [("PPP", "POLITICAL_PARTY"), ("Sukkur", "CITY"), ("Thursday", "DATE")],
    "TFN-TST4-0013": [("Lahore", "CITY"), ("Sialkot", "CITY"), ("M-11 Motorway", "LANDMARK_FACILITY")],
    "TFN-TST4-0014": [("Lahore Expo Centre", "LANDMARK_FACILITY"), ("JUI-F", "POLITICAL_PARTY")],
    "TFN-TST4-0015": [("Income Tax Ordinance, 2001", "LAW_ACT"), ("Saad Qureshi", "PERSON")],
    "TFN-TST4-0016": [("26.5%", "PERCENT"), ("September", "DATE"), ("State Bank of Pakistan", "GOVERNMENT_BODY")],
    "TFN-TST4-0017": [("Bushra Malik", "PERSON"), ("19th December", "DATE"), ("04:15 PM", "TIME")],
    "TFN-TST4-0018": [("Oman", "COUNTRY"), ("Systems Limited", "ORGANIZATION"), ("Rs890", "MONEY")],
    "TFN-TST4-0019": [("New Zealand", "SPORTS_TEAM"), ("South Africa", "SPORTS_TEAM"), ("Gaddafi Stadium", "LANDMARK_FACILITY"), ("10th of May", "DATE")],
    "TFN-TST4-0020": [("Ayesha Ghani", "PERSON"), ("Fauji Fertilizer", "ORGANIZATION"), ("12 June 2027", "DATE")],
    "TFN-TST4-0021": [("18.2%", "PERCENT"), ("February", "DATE"), ("Ministry of Commerce", "GOVERNMENT_BODY")],
    "TFN-TST4-0022": [("Bilal Tariq", "PERSON"), ("Zeeshan Tariq", "PERSON"), ("35202-4455667-8", "ID_NUMBER")],
    "TFN-TST4-0023": [("Samaa TV", "MEDIA_OUTLET"), ("Gwadar", "CITY"), ("7 pm", "TIME")],
    "TFN-TST4-0024": [("Australia", "SPORTS_TEAM"), ("Sri Lanka", "SPORTS_TEAM"), ("Iqbal Stadium", "LANDMARK_FACILITY"), ("15-08-25", "DATE")],
    "TFN-TST4-0025": [("25%", "PERCENT"), ("February 01, 2027", "DATE"), ("University of Karachi", "EDUCATIONAL_INSTITUTION")],
    "TFN-TST4-0026": [("Hina Baig", "PERSON"), ("(061) 4567 1234", "PHONE_NUMBER"), ("National Games", "EVENT")],
    "TFN-TST4-0027": [("Special Court", "COURT_LEGAL_BODY"), ("Rawalpindi", "CITY"), ("Daniyal Ansari", "PERSON"), ("11th of March", "DATE")],
    "TFN-TST4-0028": [("Faisalabad", "CITY"), ("22nd July", "DATE"), ("Punjab Police", "GOVERNMENT_BODY")],
    "TFN-TST4-0029": [("Multan", "CITY"), ("14/03/2027", "DATE"), ("Pakistan Telecommunication Authority", "GOVERNMENT_BODY")],
    "TFN-TST4-0030": [("Peshawar High Court", "COURT_LEGAL_BODY"), ("National Highway Authority", "GOVERNMENT_BODY"), ("Nida Abbasi", "PERSON")],
    "TFN-TST4-0031": [("Islamabad United", "SPORTS_TEAM"), ("Shadab", "PERSON"), ("Pakistan Super League", "EVENT")],
    "TFN-TST4-0032": [("Defense Day", "EVENT"), ("45 lakh rupees", "MONEY"), ("Mohatta Palace", "LANDMARK_FACILITY")],
    "TFN-TST4-0033": [("Pakistan Meteorological Department", "GOVERNMENT_BODY"), ("Rs640", "MONEY"), ("Peshawar", "CITY")],
    "TFN-TST4-0034": [("Germany", "COUNTRY"), ("Sialkot", "CITY"), ("Rs. 15 crore", "MONEY")],
    "TFN-TST4-0035": [("Sindh High Court", "COURT_LEGAL_BODY"), ("October 18, 2025", "DATE")],
    "TFN-TST4-0036": [("Islamabad Expo Centre", "LANDMARK_FACILITY"), ("Tehreek-e-Labbaik Pakistan", "POLITICAL_PARTY")],
    "TFN-TST4-0037": [("Criminal Procedure Code", "LAW_ACT"), ("Usman Brohi", "PERSON")],
    "TFN-TST4-0038": [("Rabia Bugti", "PERSON"), ("Kamran Khattak", "PERSON"), ("53201-9988776-4", "ID_NUMBER")],
    "TFN-TST4-0039": [("National Cattle Show", "EVENT"), ("Sukkur", "CITY"), ("5th March", "DATE"), ("14th of March", "DATE")],
    "TFN-TST4-0040": [("Careem", "ORGANIZATION"), ("32%", "PERCENT")],
    "TFN-TST4-0041": [("Awami National Party", "POLITICAL_PARTY"), ("PML-N", "POLITICAL_PARTY"), ("11-04-25", "DATE")],
    "TFN-TST4-0042": [("BBC", "MEDIA_OUTLET"), ("National Disaster Management Authority", "GOVERNMENT_BODY"), ("Rs. 9 crore", "MONEY"), ("Cholistan", "PROVINCE_REGION")],
    "TFN-TST4-0043": [("Zeeshan Tarar", "PERSON"), ("PPP", "POLITICAL_PARTY"), ("Gilgit-Baltistan", "PROVINCE_REGION")],
    "TFN-TST4-0044": [("Shazia Malik", "PERSON"), ("+923334445566", "PHONE_NUMBER"), ("Pakistan Day", "EVENT")],
    "TFN-TST4-0045": [("19.5%", "PERCENT"), ("10 Sep 2026", "DATE"), ("NUST", "EDUCATIONAL_INSTITUTION")],
    "TFN-TST4-0046": [("+92-51-22334455", "PHONE_NUMBER"), ("Federal Board of Revenue", "GOVERNMENT_BODY"), ("Quetta", "CITY")],
    "TFN-TST4-0047": [("Fatima Siddiqui", "PERSON"), ("Tariq Raza", "PERSON"), ("37405-1122334-9", "ID_NUMBER")],
    "TFN-TST4-0048": [("PKR 145,200", "MONEY"), ("Oil and Gas Regulatory Authority", "GOVERNMENT_BODY")],
    "TFN-TST4-0049": [("+92-91-5829102", "PHONE_NUMBER"), ("07:30 hours", "TIME"), ("15:30 hours", "TIME")],
    "TFN-TST4-0050": [("TechFest", "EVENT"), ("60 lakh rupees", "MONEY"), ("Clifton Beach", "LANDMARK_FACILITY")],
    "TFN-TST4-0051": [("Sindh", "PROVINCE_REGION"), ("35 per cent", "PERCENT"), ("August", "DATE")],
    "TFN-TST4-0052": [("Ayesha Lund", "PERSON"), ("55 million rupees", "MONEY"), ("Supreme Court of Pakistan", "COURT_LEGAL_BODY")],
    "TFN-TST4-0053": [("China", "COUNTRY"), ("21.4 percent", "PERCENT")],
    "TFN-TST4-0054": [("Edhi Foundation", "ORGANIZATION"), ("Rawalpindi", "CITY")],
    "TFN-TST4-0055": [("Accountability Court", "COURT_LEGAL_BODY"), ("Lahore", "CITY"), ("Balochistan High Court", "COURT_LEGAL_BODY"), ("12th August", "DATE")],
    "TFN-TST4-0056": [("Shazia Mirza", "PERSON"), ("PTI", "POLITICAL_PARTY"), ("KPK", "PROVINCE_REGION")],
    "TFN-TST4-0057": [("Pakistan", "SPORTS_TEAM"), ("Bangladesh", "SPORTS_TEAM"), ("Multan Cricket Stadium", "LANDMARK_FACILITY"), ("18/04/2026", "DATE")],
    "TFN-TST4-0058": [("Dawn", "MEDIA_OUTLET"), ("Engro Corporation", "ORGANIZATION"), ("14.8%", "PERCENT")],
    "TFN-TST4-0059": [("Balochistan National Party", "POLITICAL_PARTY"), ("State Bank of Pakistan", "GOVERNMENT_BODY")],
    "TFN-TST4-0060": [("Tariq Mahmood", "PERSON"), ("Jinnah International Airport", "LANDMARK_FACILITY"), ("22-10-27", "DATE")],
    "TFN-TST4-0061": [("Punjab", "PROVINCE_REGION"), ("Government of Punjab", "GOVERNMENT_BODY")],
    "TFN-TST4-0062": [("Islamabad High Court", "COURT_LEGAL_BODY"), ("Pakistan International Airlines", "ORGANIZATION"), ("Pakistan Penal Code", "LAW_ACT")],
    "TFN-TST4-0063": [("The Express Tribune", "MEDIA_OUTLET"), ("Peshawar", "CITY"), ("4 am", "TIME")],
    "TFN-TST4-0064": [("+923001122334", "PHONE_NUMBER"), ("National Accountability Bureau", "GOVERNMENT_BODY"), ("Sukkur", "CITY")],
    "TFN-TST4-0065": [("Minar-e-Pakistan", "LANDMARK_FACILITY")],
    "TFN-TST4-0066": [("Kamran Cheema", "PERSON"), ("17301-7788992-3", "ID_NUMBER"), ("Swat", "CITY")],
    "TFN-TST4-0067": [("LUMS", "EDUCATIONAL_INSTITUTION"), ("Lahore", "CITY"), ("Wednesday", "DATE")],
    "TFN-TST4-0068": [("Saudi Arabia", "COUNTRY"), ("Iran", "COUNTRY"), ("Gwadar", "CITY"), ("14 Jul 2026", "DATE")],
    "TFN-TST4-0069": [("Kiran Baloch", "PERSON"), ("PKR 450,200", "MONEY"), ("Tariq Qureshi", "PERSON"), ("19-06-26", "DATE")],
    "TFN-TST4-0070": [("Khyber Pakhtunkhwa", "PROVINCE_REGION"), ("22.5 per cent", "PERCENT")],
    "TFN-TST4-0071": [("Danish Javed", "PERSON"), ("Hyderabad", "CITY"), ("Karachi", "CITY")],
    "TFN-TST4-0072": [("Maryam Ahmed", "PERSON"), ("World Bank", "ORGANIZATION"), ("October 10, 2026", "DATE")],
    "TFN-TST4-0073": [("IBA Karachi", "EDUCATIONAL_INSTITUTION"), ("2 pm", "TIME"), ("01-12-25", "DATE")],
    "TFN-TST4-0074": [("Danish Siddiqui", "PERSON"), ("Swat", "CITY"), ("Azad Jammu and Kashmir", "PROVINCE_REGION")],
    "TFN-TST4-0075": [("Islamabad", "CITY"), ("9pm", "TIME"), ("0300-1234568", "PHONE_NUMBER")],
    "TFN-TST4-0076": [("Balochistan", "PROVINCE_REGION"), ("Pakistan Meteorological Department", "GOVERNMENT_BODY")],
    "TFN-TST4-0077": [("Shaheen Afridi", "PERSON"), ("Lahore Qalandars", "SPORTS_TEAM"), ("Karachi Kings", "SPORTS_TEAM")],
    "TFN-TST4-0078": [("NUST", "EDUCATIONAL_INSTITUTION"), ("Islamabad", "CITY"), ("15 November", "DATE")],
    "TFN-TST4-0079": [("Habib Bank Limited", "ORGANIZATION"), ("9.6 per cent", "PERCENT")],
    "TFN-TST4-0080": [("Federal Shariat Court", "COURT_LEGAL_BODY"), ("12/11/2026", "DATE")]
}

base_dir = Path(__file__).resolve().parent.parent.parent / "student_pack_techfest" / "student_pack_techfest" / "student_pack"
in_path = base_dir / "sample_benchmark_v4.jsonl"
out_gold = base_dir / "sample_benchmark_v4_gold.jsonl"

with open(in_path, encoding="utf-8") as f:
    lines = [json.loads(l) for l in f if l.strip()]

gold_rows = []
for d in lines:
    sid = d["id"]
    text = d["text"]
    expected_ents = EXPECTED_V4.get(sid, [])
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

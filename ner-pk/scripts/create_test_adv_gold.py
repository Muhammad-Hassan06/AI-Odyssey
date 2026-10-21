import json
from pathlib import Path

# Ground truth mapping for the 80 adversarial sentences
EXPECTED_ADV = {
    "TFN-ADV-0001": [("Bilal Qureshi", "PERSON"), ("35201-9988776-2", "ID_NUMBER"), ("NADRA", "GOVERNMENT_BODY")],
    "TFN-ADV-0002": [("Geo News", "MEDIA_OUTLET"), ("Punjab government", "GOVERNMENT_BODY"), ("Rs. 5 crore", "MONEY"), ("DG Khan", "CITY")],
    "TFN-ADV-0003": [("Sana Farooqui", "PERSON"), ("MQM-P", "POLITICAL_PARTY"), ("12th December 2026", "DATE")],
    "TFN-ADV-0004": [("Gilgit-Baltistan", "PROVINCE_REGION"), ("Independence Day", "EVENT")],
    "TFN-ADV-0005": [("PTI", "POLITICAL_PARTY"), ("Faisalabad", "CITY"), ("Sunday", "DATE")],
    "TFN-ADV-0006": [("NED University", "EDUCATIONAL_INSTITUTION"), ("9:15 a.m.", "TIME"), ("Monday", "DATE")],
    "TFN-ADV-0007": [("High Court", "COURT_LEGAL_BODY"), ("Peshawar", "CITY"), ("Supreme Court of Pakistan", "COURT_LEGAL_BODY"), ("14/06/2027", "DATE")],
    "TFN-ADV-0008": [("Islamabad High Court", "COURT_LEGAL_BODY"), ("Systems Limited", "ORGANIZATION"), ("Copyright Ordinance, 1962", "LAW_ACT")],
    "TFN-ADV-0009": [("+92-51-2827192", "PHONE_NUMBER"), ("10am", "TIME"), ("19:45 hours", "TIME")],
    "TFN-ADV-0010": [("Jazz", "ORGANIZATION"), ("Peshawar", "CITY")],
    "TFN-ADV-0011": [("Rs. 850 million", "MONEY"), ("Gaddafi Stadium", "LANDMARK_FACILITY")],
    "TFN-ADV-0012": [("PPP", "POLITICAL_PARTY"), ("Larkana", "CITY"), ("Friday", "DATE")],
    "TFN-ADV-0013": [("Sukkur", "CITY"), ("Multan", "CITY"), ("M-5 Motorway", "LANDMARK_FACILITY")],
    "TFN-ADV-0014": [("Islamabad Expo Centre", "LANDMARK_FACILITY")],
    "TFN-ADV-0015": [("Finance Act, 2025", "LAW_ACT"), ("Zeeshan Malik", "PERSON")],
    "TFN-ADV-0016": [("28.4%", "PERCENT"), ("July", "DATE"), ("State Bank of Pakistan", "GOVERNMENT_BODY")],
    "TFN-ADV-0017": [("Komal Ghani", "PERSON"), ("03rd November", "DATE"), ("02:30 PM", "TIME")],
    "TFN-ADV-0018": [("Dubai", "CITY"), ("Fauji Foundation", "ORGANIZATION"), ("Rs410", "MONEY")],
    "TFN-ADV-0019": [("Australia", "SPORTS_TEAM"), ("Bangladesh", "SPORTS_TEAM"), ("Iqbal Stadium", "LANDMARK_FACILITY"), ("19th of September", "DATE")],
    "TFN-ADV-0020": [("Hira Javed", "PERSON"), ("Engro Corporation", "ORGANIZATION"), ("05 May 2026", "DATE")],
    "TFN-ADV-0021": [("6.2%", "PERCENT"), ("October", "DATE"), ("Ministry of Planning", "GOVERNMENT_BODY")],
    "TFN-ADV-0022": [("Usman Abbasi", "PERSON"), ("Tariq Abbasi", "PERSON"), ("61101-2345678-9", "ID_NUMBER")],
    "TFN-ADV-0023": [("Dawn", "MEDIA_OUTLET"), ("Quetta", "CITY"), ("8 pm", "TIME")],
    "TFN-ADV-0024": [("Sri Lanka", "SPORTS_TEAM"), ("New Zealand", "SPORTS_TEAM"), ("National Stadium", "LANDMARK_FACILITY"), ("21-01-25", "DATE")],
    "TFN-ADV-0025": [("22%", "PERCENT"), ("January 10, 2027", "DATE"), ("IBA Karachi", "EDUCATIONAL_INSTITUTION")],
    "TFN-ADV-0026": [("Rabia Ansari", "PERSON"), ("(051) 5123 9874", "PHONE_NUMBER"), ("National Exhibition", "EVENT")],
    "TFN-ADV-0027": [("Banking Court", "COURT_LEGAL_BODY"), ("Multan", "CITY"), ("Daniyal Khan", "PERSON"), ("27th of March", "DATE")],
    "TFN-ADV-0028": [("Peshawar", "CITY"), ("30th June", "DATE"), ("Punjab Police", "GOVERNMENT_BODY")],
    "TFN-ADV-0029": [("Rawalpindi", "CITY"), ("12/04/2027", "DATE"), ("Pakistan Telecommunication Authority", "GOVERNMENT_BODY")],
    "TFN-ADV-0030": [("Lahore High Court", "COURT_LEGAL_BODY"), ("National Highway Authority", "GOVERNMENT_BODY"), ("Mehwish Ansari", "PERSON")],
    "TFN-ADV-0031": [("Karachi Kings", "SPORTS_TEAM"), ("Babar", "PERSON"), ("Pakistan Super League", "EVENT")],
    "TFN-ADV-0032": [("Kashmir Day", "EVENT"), ("15 lakh rupees", "MONEY"), ("Frere Hall", "LANDMARK_FACILITY")],
    "TFN-ADV-0033": [("Pakistan Meteorological Department", "GOVERNMENT_BODY"), ("Rs750", "MONEY"), ("Quetta", "CITY")],
    "TFN-ADV-0034": [("China", "COUNTRY"), ("Lahore", "CITY"), ("Rs. 12 crore", "MONEY")],
    "TFN-ADV-0035": [("Sindh High Court", "COURT_LEGAL_BODY"), ("November 04, 2025", "DATE")],
    "TFN-ADV-0036": [("Karachi Expo Centre", "LANDMARK_FACILITY"), ("JUI-F", "POLITICAL_PARTY")],
    "TFN-ADV-0037": [("Criminal Procedure Code", "LAW_ACT"), ("Asad Brohi", "PERSON")],
    "TFN-ADV-0038": [("Nadia Bugti", "PERSON"), ("Akram Khattak", "PERSON"), ("43203-1122334-5", "ID_NUMBER")],
    "TFN-ADV-0039": [("National Horse Show", "EVENT"), ("Multan", "CITY"), ("10th February", "DATE"), ("18th of February", "DATE")],
    "TFN-ADV-0040": [("Careem", "ORGANIZATION"), ("18%", "PERCENT")],
    "TFN-ADV-0041": [("Pakistan Muslim League-Nawaz", "POLITICAL_PARTY"), ("Jamaat-e-Islami", "POLITICAL_PARTY"), ("29-05-25", "DATE")],
    "TFN-ADV-0042": [("BBC", "MEDIA_OUTLET"), ("National Disaster Management Authority", "GOVERNMENT_BODY"), ("Rs. 4 crore", "MONEY"), ("Sindh", "PROVINCE_REGION")],
    "TFN-ADV-0043": [("Zafar Tarar", "PERSON"), ("PML-N", "POLITICAL_PARTY"), ("Azad Jammu and Kashmir", "PROVINCE_REGION")],
    "TFN-ADV-0044": [("Shazia Malik", "PERSON"), ("+923219988776", "PHONE_NUMBER"), ("Defense Day", "EVENT")],
    "TFN-ADV-0045": [("15.5%", "PERCENT"), ("01 Sep 2026", "DATE"), ("National University of Sciences and Technology", "EDUCATIONAL_INSTITUTION")],
    "TFN-ADV-0046": [("+92-21-99201122", "PHONE_NUMBER"), ("Federal Board of Revenue", "GOVERNMENT_BODY"), ("Hyderabad", "CITY")],
    "TFN-ADV-0047": [("Fatima Siddiqui", "PERSON"), ("Ahmed Raza", "PERSON"), ("37405-6677889-0", "ID_NUMBER")],
    "TFN-ADV-0048": [("PKR 112,450", "MONEY"), ("Oil and Gas Regulatory Authority", "GOVERNMENT_BODY")],
    "TFN-ADV-0049": [("+92-91-9210342", "PHONE_NUMBER"), ("08:00 hours", "TIME"), ("16:00 hours", "TIME")],
    "TFN-ADV-0050": [("TechFest", "EVENT"), ("80 lakh rupees", "MONEY"), ("Clifton Beach", "LANDMARK_FACILITY")],
    "TFN-ADV-0051": [("Balochistan", "PROVINCE_REGION"), ("28 per cent", "PERCENT"), ("August", "DATE")],
    "TFN-ADV-0052": [("Ayesha Lund", "PERSON"), ("45 million rupees", "MONEY"), ("Supreme Court of Pakistan", "COURT_LEGAL_BODY")],
    "TFN-ADV-0053": [("Saudi Arabia", "COUNTRY"), ("19.3 percent", "PERCENT")],
    "TFN-ADV-0054": [("Edhi Foundation", "ORGANIZATION"), ("Rawalpindi", "CITY")],
    "TFN-ADV-0055": [("Accountability Court", "COURT_LEGAL_BODY"), ("Lahore", "CITY"), ("Balochistan High Court", "COURT_LEGAL_BODY"), ("16th August", "DATE")],
    "TFN-ADV-0056": [("Shazia Mirza", "PERSON"), ("PTI", "POLITICAL_PARTY"), ("Punjab", "PROVINCE_REGION")],
    "TFN-ADV-0057": [("Pakistan", "SPORTS_TEAM"), ("New Zealand", "SPORTS_TEAM"), ("Multan Cricket Stadium", "LANDMARK_FACILITY"), ("15/03/2026", "DATE")],
    "TFN-ADV-0058": [("Dawn", "MEDIA_OUTLET"), ("Systems Limited", "ORGANIZATION"), ("16.2%", "PERCENT")],
    "TFN-ADV-0059": [("Balochistan National Party", "POLITICAL_PARTY"), ("State Bank of Pakistan", "GOVERNMENT_BODY")],
    "TFN-ADV-0060": [("Tariq Mahmood", "PERSON"), ("Jinnah International Airport", "LANDMARK_FACILITY"), ("18-09-27", "DATE")],
    "TFN-ADV-0061": [("Punjab", "PROVINCE_REGION"), ("Government of Punjab", "GOVERNMENT_BODY")],
    "TFN-ADV-0062": [("Islamabad High Court", "COURT_LEGAL_BODY"), ("Pakistan International Airlines", "ORGANIZATION"), ("Pakistan Penal Code", "LAW_ACT")],
    "TFN-ADV-0063": [("The Express Tribune", "MEDIA_OUTLET"), ("Peshawar", "CITY"), ("5 am", "TIME")],
    "TFN-ADV-0064": [("+923124567890", "PHONE_NUMBER"), ("National Accountability Bureau", "GOVERNMENT_BODY"), ("Sukkur", "CITY")],
    "TFN-ADV-0065": [("Minar-e-Pakistan", "LANDMARK_FACILITY")],
    "TFN-ADV-0066": [("Kamran Cheema", "PERSON"), ("17301-4455667-1", "ID_NUMBER"), ("Swat", "CITY")],
    "TFN-ADV-0067": [("LUMS", "EDUCATIONAL_INSTITUTION"), ("Lahore", "CITY"), ("Thursday", "DATE")],
    "TFN-ADV-0068": [("Saudi Arabia", "COUNTRY"), ("China", "COUNTRY"), ("Gwadar", "CITY"), ("22 Jul 2026", "DATE")],
    "TFN-ADV-0069": [("Kiran Baloch", "PERSON"), ("PKR 350,400", "MONEY"), ("Tariq Qureshi", "PERSON"), ("11-05-26", "DATE")],
    "TFN-ADV-0070": [("Khyber Pakhtunkhwa", "PROVINCE_REGION"), ("24.1 per cent", "PERCENT")],
    "TFN-ADV-0071": [("Danish Javed", "PERSON"), ("Hyderabad", "CITY"), ("Karachi", "CITY")],
    "TFN-ADV-0072": [("Maryam Ahmed", "PERSON"), ("World Bank", "ORGANIZATION"), ("September 12, 2026", "DATE")],
    "TFN-ADV-0073": [("IBA Karachi", "EDUCATIONAL_INSTITUTION"), ("3 pm", "TIME"), ("04-11-25", "DATE")],
    "TFN-ADV-0074": [("Danish Siddiqui", "PERSON"), ("Swat", "CITY"), ("Azad Jammu and Kashmir", "PROVINCE_REGION")],
    "TFN-ADV-0075": [("Islamabad", "CITY"), ("10pm", "TIME"), ("0300-8765432", "PHONE_NUMBER")],
    "TFN-ADV-0076": [("Sindh", "PROVINCE_REGION"), ("Pakistan Meteorological Department", "GOVERNMENT_BODY")],
    "TFN-ADV-0077": [("Shaheen Afridi", "PERSON"), ("Lahore Qalandars", "SPORTS_TEAM"), ("Islamabad United", "SPORTS_TEAM")],
    "TFN-ADV-0078": [("NUST", "EDUCATIONAL_INSTITUTION"), ("Islamabad", "CITY"), ("30 November", "DATE")],
    "TFN-ADV-0079": [("Habib Bank Limited", "ORGANIZATION"), ("11.4 per cent", "PERCENT")],
    "TFN-ADV-0080": [("Federal Shariat Court", "COURT_LEGAL_BODY"), ("25/10/2026", "DATE")]
}

base_dir = Path(__file__).resolve().parent.parent.parent / "student_pack_techfest" / "student_pack_techfest" / "student_pack"
in_path = base_dir / "sample_test_adv.jsonl"
out_gold = base_dir / "sample_test_adv_gold.jsonl"

with open(in_path, encoding="utf-8") as f:
    lines = [json.loads(l) for l in f if l.strip()]

gold_rows = []
for d in lines:
    sid = d["id"]
    text = d["text"]
    expected_ents = EXPECTED_ADV.get(sid, [])
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

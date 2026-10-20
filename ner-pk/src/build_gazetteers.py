"""
Pakistani Entities Gazetteer Builder (Bilingual English & Urdu).
Generates comprehensive JSON gazetteers for closed-class and domain-specific categories
with full English, Urdu script, and common abbreviation coverage.
"""

import os
import json

GAZETTEER_DIR = os.path.join(os.path.dirname(__file__), "gazetteers")
os.makedirs(GAZETTEER_DIR, exist_ok=True)

GAZETTEERS = {
    "provinces": [
        # English
        "Punjab", "Sindh", "Khyber Pakhtunkhwa", "KP", "KPK", "Balochistan",
        "Gilgit-Baltistan", "GB", "Azad Jammu and Kashmir", "Azad Kashmir", "AJK",
        "Islamabad Capital Territory", "ICT", "FATA", "Potohar", "Thar Desert",
        "Saraiki belt", "Hazara",
        # Urdu
        "پنجاب", "سندھ", "خیبر پختونخوا", "خیبر پختونخواہ", "بلوچستان", "گلگت بلتستان",
        "آزاد جموں و کشمیر", "آزاد کشمیر", "قبائلی اضلاع", "اسلام آباد کیپیٹل ٹیریٹری",
        "خطہ پوٹھوہار", "پوٹھوہار", "صحرائے تھر", "سرائیکی خطہ", "ہزارہ", "فاٹا"
    ],
    "cities": [
        # English
        "Karachi", "Lahore", "Faisalabad", "Rawalpindi", "Gujranwala", "Peshawar",
        "Multan", "Hyderabad", "Islamabad", "Quetta", "Bahawalpur", "Sargodha",
        "Sialkot", "Sukkur", "Larkana", "Sheikhupura", "Rahim Yar Khan", "Jhang",
        "Dera Ghazi Khan", "Gujrat", "Sahiwal", "Wah Cantonment", "Mardan", "Kasur",
        "Okara", "Mingora", "Nawabshah", "Chiniot", "Kotri", "Kamoke", "Hafizabad",
        "Sadiqabad", "Mirpur Khas", "Burewala", "Kohat", "Khanewal", "Dera Ismail Khan",
        "Turbat", "Muzaffargarh", "Abbottabad", "Mandi Bahauddin", "Shikarpur",
        "Jacobabad", "Jhelum", "Khanpur", "Khairpur", "Khuzdar", "Pakpattan", "Hub",
        "Daska", "Gojra", "Dadu", "Muridke", "Bahawalnagar", "Samundri", "Tando Allahyar",
        "Tando Adam", "Jaranwala", "Chishtian", "Muzaffarabad", "Attock", "Vehari",
        "Chakwal", "Wazirabad", "Mansehra", "Layyah", "Swabi", "Chaman", "Taxila",
        "Nowshera", "Khushab", "Mianwali", "Lodhran", "Hasilpur", "Charsadda", "Bhakkar",
        "Badin", "Ghotki", "Narowal", "Tando Muhammad Khan", "Mirpur", "Gwadar", "Ziarat",
        "Gilgit", "Skardu",
        # Urdu
        "کراچی", "لاہور", "فیصل آباد", "راولپنڈی", "گوجرانوالہ", "پشاور", "ملتان", "حیدرآباد",
        "اسلام آباد", "کوئٹہ", "بہاولپور", "سرگودھا", "سیالکوٹ", "سکھر", "لاڑکانہ", "شیخوپورہ",
        "رحیم یار خان", "جھنگ", "ڈیرہ غازی خان", "گجرات", "ساہیوال", "واہ کینٹ", "مردان",
        "قصور", "اوکاڑہ", "مینگورہ", "نواب شاہ", "چنیوٹ", "کوٹری", "کامونکی", "حافظ آباد",
        "صادق آباد", "میرپور خاص", "بورے والا", "کوہاٹ", "خانیوال", "ڈیرہ اسماعیل خان", "تربت",
        "مظفر گڑھ", "ایبٹ آباد", "منڈی بہاؤالدین", "شکارپور", "جیکب آباد", "جہلم", "خانپور",
        "خیرپور", "خضدار", "پاکپتن", "حب", "ڈسکہ", "گوجرہ", "دادو", "مریدکے", "بہاولنگر",
        "سمندری", "ٹنڈو الہ یار", "ٹنڈو آدم", "جڑانوالہ", "چشتیاں", "مظفر آباد", "اٹک", "وہاڑی",
        "چکوال", "وزیرآباد", "مانسہرہ", "لیہ", "صوابی", "چمن", "ٹیکسلا", "نوشہرہ", "خوشاب",
        "میانوالی", "لودھراں", "حاصل پور", "چارسدہ", "بھکر", "بدین", "گھوٹکی", "نارووال",
        "ٹنڈو محمد خان", "میرپور", "گوادر", "زیارت", "گلگت", "سکردو"
    ],
    "political_parties": [
        # English
        "Pakistan Tehreek-e-Insaf", "PTI", "Pakistan Muslim League (N)", "PML-N", "PMLN",
        "Pakistan Peoples Party", "PPP", "Muttahida Qaumi Movement", "MQM", "MQM-P",
        "Jamaat-e-Islami", "JI", "Jamiat Ulema-e-Islam", "JUI-F", "JUI", "Awami National Party",
        "ANP", "Balochistan National Party", "BNP", "BNP-Mengal", "Balochistan Awami Party",
        "BAP", "Istehkam-e-Pakistan Party", "IPP", "Tehreek-e-Labbaik Pakistan", "TLP",
        "Pakistan Muslim League (Q)", "PML-Q", "PMLQ", "Pashtunkhwa Milli Awami Party",
        "PkMAP", "Pakistan Democratic Movement", "PDM",
        # Urdu
        "پاکستان تحریک انصاف", "تحریک انصاف", "پی ٹی آئی", "مسلم لیگ ن", "پاکستان مسلم لیگ ن",
        "مسلم لیگ (ن)", "پاکستان پیپلز پارٹی", "پیپلز پارٹی", "پی پی پی", "متحدہ قومی موومنٹ",
        "ایم کیو ایم", "ایم کیو ایم پاکستان", "جماعت اسلامی", "جے آئی", "جمعیت علمائے اسلام",
        "جے یو آئی", "جے یو آئی ف", "عوامی نیشنل پارٹی", "اے این پی", "بلوچستان نیشنل پارٹی",
        "بی این پی", "بلوچستان عوامی پارٹی", "بی اے پی", "استحکام پاکستان پارٹی", "آئی پی پی",
        "تحریک لبیک پاکستان", "ٹی ایل پی", "پاکستان مسلم لیگ ق", "مسلم لیگ ق", "پی ڈی ایم",
        "پختونخوا ملی عوامی پارٹی", "پاکستان ڈیموکریٹک موومنٹ"
    ],
    "courts": [
        # English
        "Supreme Court of Pakistan", "Supreme Court", "SC", "SCP",
        "Lahore High Court", "LHC", "Sindh High Court", "SHC",
        "Peshawar High Court", "PHC", "Islamabad High Court", "IHC",
        "Balochistan High Court", "BHC", "Federal Shariat Court", "FSC",
        "Judicial Commission of Pakistan", "JCP", "Supreme Judicial Council", "SJC",
        "National Accountability Court", "Accountability Court",
        "Anti-Terrorism Court", "ATC", "Banking Court", "Customs Appellate Tribunal",
        # Urdu
        "عدالت عظمیٰ پاکستان", "عدالت عظمیٰ", "سپریم کورٹ آف پاکستان", "سپریم کورٹ",
        "لاہور ہائیکورٹ", "لاہور ہائی کورٹ", "سندھ ہائیکورٹ", "سندھ ہائی کورٹ",
        "اسلام آباد ہائیکورٹ", "اسلام آباد ہائی کورٹ", "پشاور ہائیکورٹ", "پشاور ہائی کورٹ",
        "بلوچستان ہائیکورٹ", "بلوچستان ہائی کورٹ", "وفاقی شرعی عدالت", "جوڈیشل کمیشن آف پاکستان",
        "سپریم جوڈیشل کونسل", "احتساب عدالت", "قومی احتساب عدالت", "انسداد دہشت گردی عدالت",
        "بینکنگ کورٹ", "کسٹمز ایپلیٹ ٹربیونل"
    ],
    "government_bodies": [
        # English
        "Federal Board of Revenue", "FBR", "State Bank of Pakistan", "SBP",
        "National Database and Registration Authority", "NADRA",
        "Securities and Exchange Commission of Pakistan", "SECP",
        "Oil and Gas Regulatory Authority", "OGRA",
        "National Accountability Bureau", "NAB",
        "Election Commission of Pakistan", "ECP",
        "Ministry of Finance", "Ministry of Foreign Affairs", "Ministry of Interior",
        "Ministry of Defence", "Ministry of Planning, Development and Special Initiatives",
        "Pakistan Bureau of Statistics", "PBS",
        "Pakistan Telecommunication Authority", "PTA",
        "Civil Aviation Authority", "CAA", "Pakistan Customs",
        "National Highway Authority", "NHA", "Water and Power Development Authority", "WAPDA",
        "National Disaster Management Authority", "NDMA",
        "Board of Investment", "BOI", "Federal Investigation Agency", "FIA",
        # Urdu
        "وفاقی حکومت", "حکومت پاکستان", "حکومت سندھ", "حکومت پنجاب", "حکومت خیبر پختونخوا",
        "حکومت بلوچستان", "فیڈرل بورڈ آف ریونیو", "ایف بی آر", "اسٹیٹ بینک آف پاکستان", "اسٹیٹ بینک",
        "نیشنل ڈیٹا بیس اینڈ رجسٹریشن اتھارٹی", "نادرا", "سیکورٹیز اینڈ ایکسچینج کمیشن آف پاکستان",
        "ایس ای سی پی", "آئل اینڈ گیس ریگولیٹری اتھارٹی", "اوگرا", "قومی احتساب بیورو", "نیب",
        "الیکشن کمیشن آف پاکستان", "الیکشن کمیشن", "ای سی پی", "وزارت خزانہ", "وزارت خارجہ",
        "وزارت داخلہ", "وزارت دفاع", "وزارت منصوبہ بندی", "ادارہ شماریات پاکستان",
        "پاکستان ٹیلی کمیونیکیشن اتھارٹی", "پی ٹی اے", "سول ایوی ایشن اتھارٹی", "سی اے اے",
        "پاکستان کسٹمز", "نیشنل ہائی وے اتھارٹی", "این ایچ اے", "واپڈا", "این ڈی ایم اے",
        "بورڈ آف انویسٹمنٹ", "وفاقی تحقیقاتی ادارہ", "ایف آئی اے"
    ],
    "educational_institutions": [
        # English
        "Lahore University of Management Sciences", "LUMS",
        "Quaid-i-Azam University", "QAU",
        "National University of Sciences and Technology", "NUST",
        "NED University of Engineering and Technology", "NEDUET", "NED University",
        "Institute of Business Administration", "IBA", "IBA Karachi",
        "University of the Punjab", "Punjab University", "PU",
        "FAST-NUCES", "FAST University", "NUCES",
        "Ghulam Ishaq Khan Institute", "GIKI",
        "Aga Khan University", "AKU",
        "COMSATS University Islamabad", "COMSATS",
        "University of Karachi", "UoK", "Karachi University",
        "King Edward Medical University", "KEMU",
        "Dow University of Health Sciences", "DUHS",
        "Allama Iqbal Open University", "AIOU",
        "University of Engineering and Technology, Lahore", "UET Lahore",
        # Urdu
        "لاہور یونیورسٹی آف مینجمنٹ سائنسز", "لمز", "قائد اعظم یونیورسٹی", "نیشنل یونیورسٹی آف سائنسز اینڈ ٹیکنالوجی",
        "نسٹ", "این ای ڈی یونیورسٹی آف انجینئرنگ اینڈ ٹیکنالوجی", "این ای ڈی یونیورسٹی", "این ای ڈی",
        "انسٹیٹیوٹ آف بزنس ایڈمنسٹریشن", "آئی بی اے کراچی", "آئی بی اے", "پنجاب یونیورسٹی", "جامعہ پنجاب",
        "فاسٹ یونیورسٹی", "فاسٹ نسٹ", "غلام اسحاق خان انسٹیٹیوٹ", "جی آئی کے", "آغا خان یونیورسٹی",
        "کامسیٹس یونیورسٹی", "کامسیٹس", "جامعہ کراچی", "کراچی یونیورسٹی", "کنگ ایڈورڈ میڈیکل یونیورسٹی",
        "ڈاؤ یونیورسٹی آف ہیلتھ سائنسز", "علامہ اقبال اوپن یونیورسٹی", "یو ای ٹی لاہور"
    ],
    "media_outlets": [
        # English
        "Dawn", "The Express Tribune", "The News International", "The News",
        "Business Recorder", "Pakistan Today", "Daily Times", "The Nation",
        "Geo News", "Geo TV", "ARY News", "ARY Digital", "Samaa TV", "Samaa",
        "Dunya News", "Hum News", "BOL News", "Express News", "92 News",
        "PTV News", "Pakistan Television Corporation", "PTV", "Radio Pakistan",
        "Associated Press of Pakistan", "APP",
        "Daily Jang", "Jang", "Nawa-i-Waqt", "Daily Express", "Daily Khabrain",
        "BBC Urdu", "Independent Urdu",
        # Urdu
        "روزنامہ جنگ", "جنگ", "نوائے وقت", "ایکسپریس نیوز", "روزنامہ ایکسپریس", "روزنامہ دنیا",
        "دنیا نیوز", "ڈان نیوز", "ڈان", "دی ایکسپریس ٹریبیون", "دی نیوز", "بزنس ریکارڈر",
        "پاکستان ٹوڈے", "جیو نیوز", "جیو ٹی وی", "اے آر وائی نیوز", "اے آر وائی", "سماء ٹی وی",
        "سماء", "ہم نیوز", "بول نیوز", "92 نیوز", "پی ٹی وی نیوز", "پاکستان ٹیلی ویژن",
        "پی ٹی وی", "ریڈیو پاکستان", "اے پی پی", "بی بی سی اردو", "انڈیپنڈنٹ اردو"
    ],
    "sports_teams": [
        # English
        "Pakistan National Cricket Team", "Pakistan Cricket Team", "Pakistan Men's Cricket Team",
        "Pakistan Women's Cricket Team", "Shaheens", "Pakistan Shaheens",
        "Karachi Kings", "Lahore Qalandars", "Islamabad United",
        "Peshawar Zalmi", "Multan Sultans", "Quetta Gladiators",
        "Pakistan National Hockey Team", "Pakistan Hockey Team",
        "Pakistan National Football Team", "WAPDA FC", "KRL FC",
        # Urdu
        "پاکستان قومی کرکٹ ٹیم", "پاکستان کرکٹ ٹیم", "قومی کرکٹ ٹیم", "شاہینز", "پاکستان شاہینز",
        "کراچی کنگز", "لاہور قلندرز", "اسلام آباد یونائیٹڈ", "پشاور زلمی", "ملتان سلطانز",
        "کوئٹہ گلیڈی ایٹرز", "پاکستان قومی ہاکی ٹیم", "پاکستان ہاکی ٹیم", "پاکستان فٹ بال ٹیم",
        "واپڈا ایف سی"
    ],
    "laws": [
        # English
        "Pakistan Penal Code", "PPC", "Code of Criminal Procedure", "CrPC",
        "Constitution of Pakistan", "1973 Constitution",
        "26th Constitutional Amendment", "26th Amendment", "18th Constitutional Amendment", "18th Amendment",
        "Prevention of Electronic Crimes Act", "PECA 2016", "PECA",
        "Anti-Terrorism Act 1997", "Anti-Terrorism Act", "ATA",
        "National Accountability Ordinance", "NAO 1999",
        "Elections Act 2017", "Income Tax Ordinance 2001", "Sales Tax Act 1990",
        "Foreign Exchange Regulation Act", "Anti-Money Laundering Act", "AMLA",
        # Urdu
        "آئین پاکستان", "دستور پاکستان", "1973 کا آئین", "26 ویں آئینی ترمیم", "18 ویں آئینی ترمیم",
        "مجموعہ تعزیرات پاکستان", "تعزیرات پاکستان", "ضابطہ فوجداری", "پیکا ایکٹ 2016", "پیکا ایکٹ",
        "انسداد دہشت گردی ایکٹ 1997", "نیب آرڈیننس 1999", "الیکشنز ایکٹ 2017",
        "انکم ٹیکس آرڈیننس 2001", "سیلز ٹیکس ایکٹ", "اینٹی منی لانڈرنگ ایکٹ"
    ],
    "landmarks": [
        # English
        "Minar-e-Pakistan", "Badshahi Mosque", "Faisal Mosque", "Mazar-e-Quaid",
        "Jinnah International Airport", "Allama Iqbal International Airport",
        "Islamabad International Airport", "Karachi Port", "Port Qasim", "Gwadar Port",
        "National Stadium Karachi", "Gaddafi Stadium", "Rawalpindi Cricket Stadium",
        "Multan Cricket Stadium", "Arbab Niaz Stadium",
        "Shaukat Khanum Memorial Cancer Hospital", "Jinnah Post Graduate Medical Centre", "JPMC",
        "Pakistan Institute of Medical Sciences", "PIMS",
        "M-2 Motorway", "M-9 Motorway", "Karakoram Highway", "KKH",
        "Tarbela Dam", "Mangla Dam", "Bhasha Dam",
        # Urdu
        "مینار پاکستان", "مزار قائد", "بادشاہی مسجد", "فیصل مسجد", "جناح انٹرنیشنل ایئرپورٹ",
        "علامہ اقبال انٹرنیشنل ایئرپورٹ", "اسلام آباد انٹرنیشنل ایئرپورٹ", "کراچی پورٹ",
        "پورٹ قاسم", "گوادر پورٹ", "نیشنل اسٹیڈیم کراچی", "قذافی اسٹیڈیم لاہور",
        "راولپنڈی کرکٹ اسٹیڈیم", "ملتان کرکٹ اسٹیڈیم", "ارباب نیاز اسٹیڈیم",
        "شوکت خانم میموریل ہسپتال", "جناح ہسپتال", "پمز ہسپتال", "ایم 2 موٹروے", "ایم 9 موٹروے",
        "شاہراہ قراقرم", "تربیلا ڈیم", "منگلا ڈیم", "بھاشا ڈیم"
    ]
}

def build_all_gazetteers():
    for name, entries in GAZETTEERS.items():
        filepath = os.path.join(GAZETTEER_DIR, f"{name}.json")
        unique_entries = list(dict.fromkeys(entries))
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(unique_entries, f, ensure_ascii=False, indent=2)
        print(f"Generated bilingual gazetteer '{name}': {len(unique_entries)} entries -> {filepath}")

if __name__ == "__main__":
    build_all_gazetteers()

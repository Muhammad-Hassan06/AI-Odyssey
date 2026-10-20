import os

GAZ_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "gazetteers")
os.makedirs(GAZ_DIR, exist_ok=True)

GAZETTEERS = {
    "cities.txt": [
        "Karachi", "Lahore", "Faisalabad", "Rawalpindi", "Gujranwala", "Peshawar", "Multan", "Hyderabad",
        "Islamabad", "Quetta", "Bahawalpur", "Sargodha", "Sialkot", "Sukkur", "Larkana", "Sheikhupura",
        "Rahim Yar Khan", "Jhang", "Dera Ghazi Khan", "Gujrat", "Sahiwal", "Wah Cantonment", "Mardan",
        "Kasur", "Okara", "Mingora", "Nawabshah", "Chiniot", "Kotri", "Kāmoke", "Hafizabad", "Sadiqabad",
        "Mirpur Khas", "Burewala", "Kohat", "Khanewal", "Dera Ismail Khan", "Turbat", "Muzaffargarh",
        "Abbottabad", "Mandi Bahauddin", "Shikarpur", "Jacobabad", "Jhelum", "Khanpur", "Khairpur",
        "Khuzdar", "Pakpattan", "Hub", "Daska", "Gojra", "Dadu", "Muridke", "Bahawalnagar", "Samundri",
        "Tando Allahyar", "Tando Adam", "Jaranwala", "Chishtian", "Muzaffarabad", "Attock", "Vehari",
        "Kot Abdul Malik", "Ferozwala", "Chakwal", "Guiranwala Cantonment", "Kamalia", "Umerkot",
        "Ahmedpur East", "Kot Addu", "Wazirabad", "Mansehra", "Layyah", "Mirpur", "Swabi", "Chaman",
        "Taxila", "Nowshera", "Khushab", "Shahdadkot", "Mianwali", "Kabal", "Lodhran", "Hasilpur",
        "Hassan Abdal", "Bhakkar", "Badin", "Zhob", "Haripur", "Gwadar", "Gilgit", "Skardu",
        "کراچی", "لاہور", "فیصل آباد", "راولپنڈی", "گوجرانوالہ", "پشاور", "ملتان", "حیدرآباد",
        "اسلام آباد", "کوئٹہ", "بہاولپور", "سرگودھا", "سیالکوٹ", "سکھر", "لاڑکانہ", "شیخوپورہ",
        "رحیم یار خان", "جھنگ", "ڈیرہ غازی خان", "گجرات", "ساہیوال", "مردان", "قصور", "اوکاڑہ",
        "مینگورہ", "نواب شاہ", "چنیوٹ", "حافظ آباد", "صادق آباد", "میرپور خاص", "بورے والا",
        "کوہاٹ", "خانیوال", "ڈیرہ اسماعیل خان", "تربت", "مظفر گڑھ", "ایبٹ آباد", "منڈی بہاؤالدین",
        "شکارپور", "یعقوب آباد", "جہلم", "خانپور", "خیرپور", "خضدار", "پاکپتن", "حب", "ڈسکہ",
        "گوجرہ", "دادو", "مریدکے", "بہاولنگر", "سمندری", "ٹنڈو الہ یار", "ٹنڈو آدم", "جڑانوالہ",
        "مظفرآباد", "اٹک", "وہاڑی", "چکوال", "کمالیہ", "عمرکوٹ", "احمد پور شرقیہ", "کوٹ ادو",
        "وزیر آباد", "مانسہرہ", "لیہ", "میرپور", "صوابی", "چمن", "ٹیکسلا", "نوشہرہ", "خوشاب",
        "شہدادکوٹ", "میانوالی", "لودھراں", "حاصل پور", "حسن ابدال", "بھکر", "بدین", "ژوب", "ہری پور",
        "گوادر", "گلگت", "سکردو"
    ],
    "provinces.txt": [
        "Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan", "Islamabad Capital Territory",
        "Gilgit-Baltistan", "Azad Jammu and Kashmir", "Azad Kashmir", "KPK", "ICT", "FATA",
        "پنجاب", "سندھ", "خیبر پختونخوا", "بلوچستان", "وفاقی دارالحکومت", "گلگت بلتستان", "آزاد کشمیر"
    ],
    "political_parties.txt": [
        "Pakistan Tehreek-e-Insaf", "PTI", "Pakistan Muslim League (Nawaz)", "PML-N", "PMLN",
        "Pakistan Peoples Party", "PPP", "Muttahida Qaumi Movement", "MQM", "MQM-P",
        "Jamiat Ulema-e-Islam (F)", "JUI-F", "Jamaat-e-Islami", "JI", "Awami National Party", "ANP",
        "Balochistan Awami Party", "BAP", "Tehreek-e-Labbaik Pakistan", "TLP", "PML-Q", "PML-F",
        "پاکستان تحریک انصاف", "تحریک انصاف", "مسلم لیگ ن", "پاکستان پیپلز پارٹی", "پیپلز پارٹی",
        "متحدہ قومی موومنٹ", "ایم کیو ایم", "جمعیت علمائے اسلام", "جماعت اسلامی", "عوامی نیشنل پارٹی"
    ],
    "courts.txt": [
        "Supreme Court of Pakistan", "Supreme Court", "Lahore High Court", "LHC", "Sindh High Court", "SHC",
        "Islamabad High Court", "IHC", "Peshawar High Court", "PHC", "Balochistan High Court", "BHC",
        "Federal Shariat Court", "Anti-Terrorism Court", "ATC", "Accountability Court", "Special Court",
        "Sessions Court", "Civil Court", "High Court",
        "عدالت عظمیٰ", "سپریم کورٹ آف پاکستان", "سپریم کورٹ", "لاہور ہائی کورٹ", "سندھ ہائی کورٹ",
        "اسلام آباد ہائی کورٹ", "پشاور ہائی کورٹ", "بلوچستان ہائی کورٹ", "وفاقی شرعی عدالت", "احتساب عدالت"
    ],
    "laws.txt": [
        "Pakistan Penal Code", "PPC", "Code of Criminal Procedure", "CrPC", "Constitution of Pakistan",
        "Anti-Terrorism Act 1997", "ATA", "Prevention of Electronic Crimes Act", "PECA 2016", "PECA",
        "National Accountability Ordinance", "NAO 1999", "Elections Act 2017", "Income Tax Ordinance 2001",
        "Companies Act 2017", "State Bank of Pakistan Act", "18th Constitutional Amendment",
        "26th Constitutional Amendment", "Customs Act 1969", "Finance Act",
        "مجموعہ تعزیرات پاکستان", "آئین پاکستان", "پیکا ایکٹ", "الیکشن ایکٹ", "اینٹی ٹیررازم ایکٹ"
    ],
    "sports_teams.txt": [
        "Pakistan National Cricket Team", "Pakistan Cricket Team", "Pakistan Hockey Team", "Shaheens",
        "Karachi Kings", "Lahore Qalandars", "Islamabad United", "Peshawar Zalmi", "Multan Sultans",
        "Quetta Gladiators", "Rawalpindi Rams", "Sialkot Stallions", "WAPDA", "KRL", "SSGC",
        "پاکستان کرکٹ ٹیم", "کراچی کنگز", "لاہور قلندرز", "اسلام آباد یونائیٹڈ", "پشاور زلمی", "ملتان سلطانز", "کوئٹہ گلیڈی ایٹرز"
    ],
    "universities.txt": [
        "Lahore University of Management Sciences", "LUMS", "National University of Sciences and Technology", "NUST",
        "Quaid-i-Azam University", "QAU", "NED University of Engineering and Technology", "NED",
        "Institute of Business Administration", "IBA", "University of the Punjab", "Punjab University", "PU",
        "University of Karachi", "KU", "Aga Khan University", "AKU", "FAST-NUCES", "FAST", "COMSATS",
        "University of Engineering and Technology", "UET Lahore", "UET Peshawar", "Government College University", "GCU",
        "جامعہ کراچی", "پنجاب یونیورسٹی", "قائد اعظم یونیورسٹی", "لمز", "نسٹ", "آغا خان یونیورسٹی"
    ],
    "media_outlets.txt": [
        "Dawn", "The News International", "The Express Tribune", "Business Recorder", "Pakistan Today",
        "The Nation", "Daily Times", "Geo News", "ARY News", "Samaa TV", "Dunya News", "Hum News",
        "Express News", "Bol News", "Daily Jang", "Daily Express", "Nawa-i-Waqt", "BBC Urdu", "PTV News",
        "ڈان", "دی نیوز", "ایکسپریس ٹریبیون", "جیو نیوز", "اے آر وائی نیوز", "سماء ٹی وی", "دنیا نیوز",
        "روزنامہ جنگ", "روزنامہ ایکسپریس", "نوائے وقت", "بی بی سی اردو"
    ],
    "government_bodies.txt": [
        "Prime Minister's Office", "PMO", "National Assembly", "Senate of Pakistan", "Senate",
        "Election Commission of Pakistan", "ECP", "State Bank of Pakistan", "SBP",
        "Federal Board of Revenue", "FBR", "Securities and Exchange Commission of Pakistan", "SECP",
        "Pakistan Bureau of Statistics", "PBS", "Higher Education Commission", "HEC",
        "National Database and Registration Authority", "NADRA", "Pakistan Telecommunication Authority", "PTA",
        "Pakistan Electronic Media Regulatory Authority", "PEMRA", "National Disaster Management Authority", "NDMA",
        "Oil and Gas Regulatory Authority", "OGRA", "NEPRA", "Inter-Services Public Relations", "ISPR",
        "وزارت خزانہ", "الیکشن کمیشن آف پاکستان", "اسٹیٹ بینک آف پاکستان", "ایف بی آر", "نادرا", "پیمرا", "پی ٹی اے"
    ]
}

def export_gazetteers():
    for filename, entries in GAZETTEERS.items():
        filepath = os.path.join(GAZ_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for entry in sorted(list(dict.fromkeys(entries))):
                f.write(f"{entry}\n")
        print(f"Exported {len(entries)} entries to {filepath}")

if __name__ == "__main__":
    export_gazetteers()

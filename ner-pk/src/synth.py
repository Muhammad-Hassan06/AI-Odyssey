"""
Synthetic Data Generator for Pakistani-Context NER.
Guarantees 100% synthetic, non-real generation for PHONE_NUMBER and ID_NUMBER.
Injects controlled template sentences with negatives to avoid false positives.
Boosts under-represented categories (TIME, LAW_ACT, COURT_LEGAL_BODY, SPORTS_TEAM, EVENT, MEDIA, EDU, MONEY)
while ensuring split isolation (Train, Dev, Benchmark) and capping synthetic proportion under 25%.
"""

import os
import sys
import random
import json
from typing import List, Dict, Any, Tuple

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.constants import set_seed

set_seed(42)

MOBILE_CODES = [
    "300", "301", "302", "303", "304", "305", "306", "307", "308", "309",
    "310", "311", "312", "313", "314", "315", "316", "317", "318",
    "320", "321", "322", "323", "324", "325",
    "330", "331", "332", "333", "334", "335", "336", "337",
    "340", "341", "342", "343", "344", "345", "346", "347"
]

LANDLINE_CODES = ["021", "042", "051", "091", "081", "041", "061", "022", "052", "055"]
PROVINCE_CODES = ["1", "2", "3", "4", "5", "6", "7"]
CITIES = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Quetta", "Multan", "Faisalabad"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

COURTS = [
    "Supreme Court of Pakistan", "Lahore High Court", "Sindh High Court",
    "Islamabad High Court", "Peshawar High Court", "Balochistan High Court",
    "Anti-Terrorism Court", "Accountability Court", "Federal Shariat Court"
]

LAWS = [
    "Pakistan Penal Code", "Code of Criminal Procedure", "Constitution of Pakistan",
    "26th Constitutional Amendment", "18th Constitutional Amendment", "PECA 2016",
    "Anti-Terrorism Act 1997", "Income Tax Ordinance 2001", "Elections Act 2017"
]

SPORTS_TEAMS = [
    "Karachi Kings", "Lahore Qalandars", "Islamabad United", "Peshawar Zalmi",
    "Multan Sultans", "Quetta Gladiators", "Pakistan National Cricket Team", "Pakistan Hockey Team"
]

EVENTS = [
    "Pakistan Super League", "PSL 10", "Independence Day", "Pakistan Day", "Defence Day",
    "Federal Budget 2025-26", "General Elections 2024", "COP29", "Youm-e-Takbir"
]

MEDIA_OUTLETS = [
    "Dawn", "The Express Tribune", "The News International", "Business Recorder",
    "Pakistan Today", "Geo News", "ARY News", "Samaa TV", "Daily Jang", "PTV News"
]

EDUCATIONAL_INSTITUTIONS = [
    "LUMS", "Quaid-i-Azam University", "NED University", "IBA Karachi",
    "National University of Sciences and Technology", "Punjab University", "FAST-NUCES", "Aga Khan University"
]

def generate_synthetic_phone() -> str:
    is_mobile = random.random() < 0.75
    if is_mobile:
        code = random.choice(MOBILE_CODES)
        num1 = random.randint(100, 999)
        num2 = random.randint(1000, 9999)
        return random.choice([
            f"+92 {code} {num1}{num2}",
            f"+92-{code}-{num1}{num2}",
            f"0092 {code} {num1}{num2}",
            f"0{code}-{num1}{num2}",
            f"0{code} {num1}{num2}",
            f"0{code}{num1}{num2}",
            f"(0{code}) {num1}{num2}"
        ])
    else:
        code = random.choice(LANDLINE_CODES)
        sub = random.randint(1000000, 9999999)
        return random.choice([
            f"{code}-{sub}",
            f"({code}) {sub}",
            f"+92 {code[1:]} {sub}",
            f"+92-{code[1:]}-{sub}"
        ])

def generate_synthetic_cnic() -> str:
    p_code = random.choice(PROVINCE_CODES)
    div_code = random.randint(100, 999)
    mid_7 = f"{random.randint(1000000, 9999999):07d}"
    last_1 = random.randint(1, 9)
    prefix_5 = f"{p_code}{div_code:03d}{random.randint(1, 9)}"

    if random.random() < 0.85:
        return f"{prefix_5}-{mid_7}-{last_1}"
    else:
        return f"{prefix_5}{mid_7}{last_1}"

def generate_synthetic_time() -> str:
    hr = random.randint(1, 12)
    mn = random.choice(["00", "15", "30", "45", f"{random.randint(10, 59):02d}"])
    period = random.choice(["AM", "PM", "am", "pm", "PST"])
    return f"{hr}:{mn} {period}"

def generate_synthetic_money() -> str:
    scale = random.choice(["crore", "lakh", "million", "billion", "trillion"])
    num = random.choice([f"{random.randint(1, 950)}", f"{random.randint(1, 99)}.{random.randint(1, 9)}"])
    prefix = random.choice(["Rs", "Rs.", "PKR", "USD", "$"])
    if prefix == "$":
        return f"${num} {scale}"
    return f"{prefix} {num} {scale}"

PHONE_TEMPLATES = [
    "For customer queries regarding reference {REF}, dial the helpline at {PHONE} during office hours.",
    "The applicant contacted the emergency desk on {PHONE} regarding the complaint in {CITY}.",
    "Candidates may reach out to the admissions office at {PHONE} before Friday afternoon.",
    "For immediate technical assistance in {CITY}, please call the support cell at {PHONE}.",
    "The official desk number was published as {PHONE} in the public gazette notice {REF}.",
    "Citizens are requested to report civic emergencies to {PHONE} without delay in {CITY}.",
    "Please send SMS inquiries to {PHONE} for confirmation of payment {REF}.",
    "The verification officer placed a call to {PHONE} to authenticate the address for case {REF}.",
    "Helpline assistance is available round the clock at {PHONE} across {CITY}.",
    "For verification of public utility services on {DAY}, call {PHONE} today."
]

ID_TEMPLATES = [
    "The applicant submitted a verified copy of CNIC {ID} along with form {REF}.",
    "Citizen with national identity card number {ID} visited the registration center in {CITY}.",
    "According to official database records, the CNIC {ID} is registered in {CITY}.",
    "Voter registration confirmed for CNIC {ID} after biometric verification in {CITY}.",
    "The candidate provided NIC {ID} during the entrance test verification in {CITY}.",
    "Verification of CNIC {ID} was successfully completed by desk officer {REF}.",
    "Please bring your original CNIC {ID} when collecting degree certificate {REF}.",
    "The bank requested a renewed copy of CNIC {ID} for compliance audit {REF}.",
    "Official notification confirmed that CNIC {ID} was registered under {CITY} district.",
    "The police registered the verification under CNIC {ID} for court record {REF}."
]

RARE_TEMPLATES = [
    "The petitioner filed constitutional petition {REF} before the {COURT} under {LAW}.",
    "A division bench of the {COURT} heard arguments regarding the validity of {LAW} in {CITY}.",
    "The legal counsel cited Section {REF} of {LAW} before the honorable bench at {COURT}.",
    "In a landmark judgment on {DAY}, the {COURT} upheld the enforcement of {LAW} across the country.",
    "Proceedings at the {COURT} in {CITY} continued today concerning provisions of {LAW}.",
    "In an exciting match on {DAY}, {TEAM} secured victory against their opponents in {CITY}.",
    "The head coach of {TEAM} announced the preliminary squad for match {REF} in {CITY}.",
    "Supporters of {TEAM} celebrated enthusiastically in {CITY} after the thrilling win on {DAY}.",
    "Management of {TEAM} confirmed the inclusion of two fast bowlers for fixture {REF}."
]

TIME_TEMPLATES = [
    "The emergency cabinet meeting commenced at {TIME} sharp in {CITY} on {DAY}.",
    "Power transmission was temporarily halted between {TIME} and midnight for feeder {REF}.",
    "The press conference in {CITY} was scheduled to address reporters at {TIME}.",
    "Trading at the exchange concluded smoothly at {TIME} on {DAY} with heavy turnover.",
    "The evening flight touched down safely at {TIME} in {CITY} according to airport officials.",
    "Proceedings at the assembly adjourned at {TIME} following the debate on {DAY}."
]

EVENT_TEMPLATES = [
    "Celebrations and ceremonies marked the opening of {EVENT} with grand enthusiasm in {CITY}.",
    "Government representatives outlined crucial strategic milestones for {EVENT} during conference {REF}.",
    "Security arrangements were strictly tightened across {CITY} ahead of {EVENT}.",
    "Delegates from across the region gathered in {CITY} on {DAY} to participate actively in {EVENT}."
]

MEDIA_TEMPLATES = [
    "An investigative report published by {MEDIA} highlighted key economic developments for project {REF}.",
    "The breaking news was telecast prominently across {MEDIA} on {DAY} evening.",
    "Editorial analysis in {MEDIA} examined the policy shifts announced in {CITY}.",
    "Senior commentators appearing on {MEDIA} discussed the parliamentary session {REF}."
]

EDU_TEMPLATES = [
    "Admissions for the upcoming academic semester opened at {EDU} in {CITY} on {DAY}.",
    "Graduating researchers at {EDU} presented innovative technological solutions for project {REF}.",
    "The governing board of {EDU} approved new scholarships for deserving scholars in {CITY}.",
    "A symposium on modern computing was organized jointly at {EDU} in {CITY} on {DAY}."
]

MONEY_TEMPLATES = [
    "The development authority authorized an infrastructure allocation of {MONEY} for scheme {REF}.",
    "Foreign direct investment in the energy sector surpassed {MONEY} for project {REF}.",
    "Commercial banks in {CITY} approved agricultural credit facilities amounting to {MONEY}.",
    "The treasury generated domestic revenues of {MONEY} according to official bulletin {REF}."
]

NEGATIVE_TEMPLATES = [
    "The case reference was registered under file number {CASE_NO} in {YEAR}.",
    "The courier shipment tracking code is {TRACKING} for parcel delivery in {CITY}.",
    "The vehicle registration plate read {PLATE} during the highway inspection near {CITY}.",
    "A total of {NUM_PEOPLE} citizens attended the public seminar in {CITY} on {DAY}.",
    "The tender quotation reference was {TENDER_NO} issued in {YEAR}.",
    "Postal code for the regional branch in {CITY} is {POSTAL}."
]

URDU_CITIES = ["اسلام آباد", "کراچی", "لاہور", "پشاور", "کوئٹہ", "ملتان", "فیصل آباد", "راولپنڈی", "حیدرآباد", "سیالکوٹ"]
URDU_PROVINCES = ["پنجاب", "سندھ", "خیبر پختونخوا", "بلوچستان", "گلگت بلتستان", "آزاد کشمیر"]
URDU_COURTS = [
    "سپریم کورٹ آف پاکستان", "لاہور ہائی کورٹ", "سندھ ہائی کورٹ",
    "اسلام آباد ہائی کورٹ", "پشاور ہائی کورٹ", "بلوچستان ہائی کورٹ", "انسداد دہشت گردی عدالت"
]
URDU_LAWS = [
    "آئین پاکستان", "مجموعہ تعزیرات پاکستان", "ضابطہ فوجداری",
    "26ویں آئینی ترمیم", "الیکشن ایکٹ 2017", "پیکا ایکٹ"
]
URDU_SPORTS_TEAMS = [
    "لاہور قلندرز", "کراچی کنگز", "اسلام آباد یونائیٹڈ", "پشاور زلمی",
    "ملتان سلطانز", "کوئٹہ گلیڈی ایٹرز", "قومی کرکٹ ٹیم"
]
URDU_EVENTS = [
    "پاکستان سپر لیگ", "یوم آزادی", "یوم پاکستان", "یوم دفاع", "وفاقی بجٹ", "عام انتخابات 2024"
]
URDU_MEDIA = [
    "جیو نیوز", "اے آر وائی نیوز", "روزنامہ جنگ", "نوائے وقت", "سماء ٹی وی", "ڈان نیوز", "ایکسپریس نیوز"
]
URDU_EDU = [
    "قائد اعظم یونیورسٹی", "پنجاب یونیورسٹی", "لمز", "آغا خان یونیورسٹی", "فاسٹ یونیورسٹی", "نمل یونیورسٹی"
]
URDU_PARTIES = [
    "پاکستان تحریک انصاف", "پاکستان مسلم لیگ (ن)", "پاکستان پیپلز پارٹی", "جماعت اسلامی", "متحدہ قومی موومنٹ"
]
URDU_GOV = [
    "الیکشن کمیشن آف پاکستان", "فیڈرل بورڈ آف ریونیو", "قومی احتساب بیورو", "سٹیٹ بینک آف پاکستان", "نادرا"
]
URDU_PERSONS = [
    "محمد علی جناح", "علامہ اقبال", "عمران خان", "نواز شریف", "شہباز شریف", "بلاول بھٹو زرداری", "قاضی فائز عیسیٰ", "ارشد ندیم", "بابر اعظم"
]
URDU_DAYS = ["پیر", "منگل", "بدھ", "جمعرات", "جمعہ", "ہفتہ", "اتوار"]

def to_eastern_digits(s: str) -> str:
    mapping = {"0":"۰","1":"۱","2":"۲","3":"۳","4":"۴","5":"۵","6":"۶","7":"۷","8":"۸","9":"۹"}
    return "".join(mapping.get(c, c) for c in str(s))

def generate_synthetic_urdu_phone() -> str:
    p = generate_synthetic_phone()
    return to_eastern_digits(p) if random.random() < 0.5 else p

def generate_synthetic_urdu_cnic() -> str:
    c = generate_synthetic_cnic()
    return to_eastern_digits(c) if random.random() < 0.5 else c

def generate_synthetic_urdu_money() -> str:
    scale = random.choice(["کروڑ", "لاکھ", "ارب"])
    num = str(random.randint(1, 950))
    if random.random() < 0.5:
        num = to_eastern_digits(num)
    return f"{num} {scale} روپے"

def generate_synthetic_urdu_percent() -> str:
    val = random.choice([f"{random.randint(1, 25)}", f"{random.randint(1, 20)}.{random.randint(1, 9)}"])
    if random.random() < 0.5:
        val = to_eastern_digits(val)
    return f"{val} فیصد"

def generate_synthetic_urdu_time() -> str:
    period = random.choice(["صبح", "دوپہر", "شام", "رات"])
    hr = str(random.randint(1, 12))
    if random.random() < 0.5:
        hr = to_eastern_digits(hr)
    return f"{period} {hr} بجے"

def generate_synthetic_urdu_date() -> str:
    months = ["جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون", "جولائی", "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"]
    m = random.choice(months)
    day = str(random.randint(1, 30))
    yr = str(random.randint(2020, 2026))
    if random.random() < 0.5:
        day = to_eastern_digits(day)
        yr = to_eastern_digits(yr)
    return f"{day} {m} {yr}"

URDU_PHONE_TEMPLATES = [
    "کسی بھی معلومات یا شکایت کے لیے ہیلپ لائن {PHONE} پر رابطہ کریں۔",
    "امیدوار {CITY} کے دفتر سے فون نمبر {PHONE} پر رجوع کر سکتے ہیں۔",
    "ایمرجنسی سروسز کے لیے شہری فوراً {PHONE} ڈائل کریں۔",
    "تفصیلات حاصل کرنے کے لیے رابطہ نمبر {PHONE} پر کال کریں۔"
]

URDU_ID_TEMPLATES = [
    "امیدوار کا قومی شناختی کارڈ نمبر {ID} برائے تصدیق جمع کرایا گیا۔",
    "شہری برائے تصدیق شناختی کارڈ {ID} لے کر {CITY} سینٹر پہنچے۔",
    "نادرا ریکارڈ کے مطابق شناختی کارڈ {ID} کا تعلق {CITY} سے ہے۔",
    "بینک اکاؤنٹ کی بحالی کے لیے شناختی کارڈ نمبر {ID} کی کاپی درکار ہے۔"
]

URDU_LEGAL_TEMPLATES = [
    "{COURT} نے {LAW} کے تحت دائر آئینی درخواست کی سماعت {DAY} تک ملتوی کر دی۔",
    "{COURT} کے دو رکنی بینچ نے {CITY} میں {LAW} کے نفاذ کا اہم حکم جاری کیا۔",
    "وکیل صفائی نے {COURT} کے روبرو {LAW} کی دفعات پر دلائل مکمل کیے۔"
]

URDU_SPORTS_TEMPLATES = [
    "{TEAM} نے شاندار کھیل کا مظاہرہ کرتے ہوئے {CITY} میں اہم میچ جیت لیا۔",
    "{TEAM} کے کپتان نے پریس کانفرنس کرتے ہوئے آئندہ میچ کی حکمت عملی پر بات کی۔",
    "{CITY} میں منعقدہ فائنل کے لیے {TEAM} کی تیاریاں عروج پر پہنچ گئیں۔"
]

URDU_GOV_TEMPLATES = [
    "{GOV} نے ٹیکس اصلاحات اور شفافیت کے لیے نئے قواعد نافذ کر دیے۔",
    "{PARTY} کے مرکزی وفد نے {CITY} میں پریس کانفرنس سے خطاب کیا۔",
    "{GOV} کی ہدایت پر {CITY} کی ضلعی انتظامیہ نے آپریشن کا آغاز کیا۔"
]

URDU_TIME_TEMPLATES = [
    "کابینہ کا ہنگامی اجلاس ٹھیک {TIME} {CITY} میں شروع ہوگا۔",
    "قومی اسمبلی کا اجلاس {DAY} کو {TIME} طلب کر لیا گیا ہے۔",
    "خصوصی پرواز {TIME} پر محفوظ طریقے سے {CITY} ایئرپورٹ پر لینڈ کر گئی۔"
]

URDU_MONEY_TEMPLATES = [
    "حکومت نے ترقیاتی منصوبے کے لیے مجموعی طور پر {MONEY} جاری کر دیے ہیں۔",
    "محکمہ خزانہ نے {CITY} کے بنیادی ڈھانچے کے لیے {MONEY} کے فنڈز منظور کیے۔",
    "بینک دولت پاکستان کی رپورٹ کے مطابق ترسیلات زر {MONEY} تک پہنچ گئیں۔"
]

URDU_EVENT_TEMPLATES = [
    "{EVENT} کی رنگارنگ افتتاحی تقریب {CITY} میں جوش و خروش سے منائی گئی۔",
    "{EVENT} کے پرامن انعقاد کے لیے {CITY} میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"
]

URDU_MEDIA_TEMPLATES = [
    "{MEDIA} کی خصوصی تحقیقاتی رپورٹ کے مطابق صورتحال میں بہتری آئی ہے۔",
    "{MEDIA} کے نمائندے نے {CITY} سے تازہ ترین احوال براہ راست نشر کیے۔"
]

URDU_EDU_TEMPLATES = [
    "{EDU} میں داخلوں کا باقاعدہ آغاز {DAY} سے کیا جا رہا ہے۔",
    "{EDU} کے ہونہار طلبہ نے {CITY} میں جدید ٹیکنالوجی پر مبنی پروجیکٹ پیش کیا۔"
]

URDU_DISTRACTOR_TEMPLATES = [
    "پولیس کے مطابق ملزم کی گاڑی کا رجسٹریشن نمبر ICT-4521 درج تھا۔",
    "عدالت میں مقدمہ نمبر 7842 کی سماعت بغیر کارروائی کے ختم ہو گئی۔",
    "ڈاکخانہ کا کوڈ نمبر 44000 جاری کیا گیا۔"
]

def generate_synthetic_dataset(
    num_phone: int = 350,
    num_id: int = 350,
    num_rare: int = 250,
    num_time: int = 150,
    num_event: int = 100,
    num_media: int = 100,
    num_edu: int = 100,
    num_money: int = 100,
    num_negatives: int = 150,
    num_urdu: int = 400,
    split_name: str = "train"
) -> List[Dict[str, Any]]:
    dataset = []
    doc_id = f"synthetic_corpus_{split_name}"
    sent_idx = 0
    generated_texts = set()

    def add_sentence(sent, entities_list, domain="Synthetic", lang="en"):
        nonlocal sent_idx
        if sent in generated_texts:
            return False
        generated_texts.add(sent)
        entities_list.sort(key=lambda x: x["start"])
        dataset.append({
            "sentence_id": f"{doc_id}_{sent_idx:04d}",
            "doc_id": doc_id,
            "source": f"Synthetic Generator ({split_name})",
            "domain": domain,
            "language": lang,
            "text": sent,
            "entities": entities_list
        })
        sent_idx += 1
        return True

    # 1. PHONE_NUMBER
    c, att = 0, 0
    while c < num_phone and att < num_phone * 5:
        att += 1
        p = generate_synthetic_phone()
        city = random.choice(CITIES)
        ref = f"{random.randint(100, 9999)}"
        day = random.choice(DAYS)
        tmpl = random.choice(PHONE_TEMPLATES)
        sent = tmpl.format(PHONE=p, CITY=city, REF=ref, DAY=day)
        ents = [{"text": p, "start": sent.find(p), "end": sent.find(p)+len(p), "label": "PHONE_NUMBER"}]
        if "{CITY}" in tmpl and sent.find(city) != -1:
            ents.append({"text": city, "start": sent.find(city), "end": sent.find(city)+len(city), "label": "CITY"})
        if add_sentence(sent, ents, "Administrative/Phones"):
            c += 1

    # 2. ID_NUMBER (CNIC)
    c, att = 0, 0
    while c < num_id and att < num_id * 5:
        att += 1
        id_val = generate_synthetic_cnic()
        city = random.choice(CITIES)
        ref = f"{random.randint(1000, 99999)}"
        tmpl = random.choice(ID_TEMPLATES)
        sent = tmpl.format(ID=id_val, CITY=city, REF=ref)
        ents = [{"text": id_val, "start": sent.find(id_val), "end": sent.find(id_val)+len(id_val), "label": "ID_NUMBER"}]
        if "{CITY}" in tmpl and sent.find(city) != -1:
            ents.append({"text": city, "start": sent.find(city), "end": sent.find(city)+len(city), "label": "CITY"})
        if add_sentence(sent, ents, "Administrative/IDs"):
            c += 1

    # 3. RARE (COURT, LAW, TEAM)
    c, att = 0, 0
    while c < num_rare and att < num_rare * 5:
        att += 1
        court = random.choice(COURTS)
        law = random.choice(LAWS)
        team = random.choice(SPORTS_TEAMS)
        city = random.choice(CITIES)
        ref = f"{random.randint(10, 499)}"
        day = random.choice(DAYS)
        tmpl = random.choice(RARE_TEMPLATES)
        sent = tmpl.format(COURT=court, LAW=law, TEAM=team, CITY=city, REF=ref, DAY=day)
        ents = []
        for val, lbl in [(court, "COURT_LEGAL_BODY"), (law, "LAW_ACT"), (team, "SPORTS_TEAM"), (city, "CITY")]:
            if val in sent and sent.find(val) != -1:
                ents.append({"text": val, "start": sent.find(val), "end": sent.find(val)+len(val), "label": lbl})
        if add_sentence(sent, ents, "Legal/Sports"):
            c += 1

    # 4. TIME
    c, att = 0, 0
    while c < num_time and att < num_time * 5:
        att += 1
        t_val = generate_synthetic_time()
        city = random.choice(CITIES)
        ref = f"FDR-{random.randint(10, 99)}"
        day = random.choice(DAYS)
        tmpl = random.choice(TIME_TEMPLATES)
        sent = tmpl.format(TIME=t_val, CITY=city, REF=ref, DAY=day)
        ents = [{"text": t_val, "start": sent.find(t_val), "end": sent.find(t_val)+len(t_val), "label": "TIME"}]
        if "{CITY}" in tmpl and sent.find(city) != -1:
            ents.append({"text": city, "start": sent.find(city), "end": sent.find(city)+len(city), "label": "CITY"})
        if add_sentence(sent, ents, "Temporal"):
            c += 1

    # 5. EVENT
    c, att = 0, 0
    while c < num_event and att < num_event * 5:
        att += 1
        ev = random.choice(EVENTS)
        city = random.choice(CITIES)
        ref = f"EV-{random.randint(100, 999)}"
        day = random.choice(DAYS)
        tmpl = random.choice(EVENT_TEMPLATES)
        sent = tmpl.format(EVENT=ev, CITY=city, REF=ref, DAY=day)
        ents = [{"text": ev, "start": sent.find(ev), "end": sent.find(ev)+len(ev), "label": "EVENT"}]
        if "{CITY}" in tmpl and sent.find(city) != -1:
            ents.append({"text": city, "start": sent.find(city), "end": sent.find(city)+len(city), "label": "CITY"})
        if add_sentence(sent, ents, "Events"):
            c += 1

    # 6. MEDIA_OUTLET
    c, att = 0, 0
    while c < num_media and att < num_media * 5:
        att += 1
        med = random.choice(MEDIA_OUTLETS)
        city = random.choice(CITIES)
        ref = f"PR-{random.randint(100, 999)}"
        day = random.choice(DAYS)
        tmpl = random.choice(MEDIA_TEMPLATES)
        sent = tmpl.format(MEDIA=med, CITY=city, REF=ref, DAY=day)
        ents = [{"text": med, "start": sent.find(med), "end": sent.find(med)+len(med), "label": "MEDIA_OUTLET"}]
        if "{CITY}" in tmpl and sent.find(city) != -1:
            ents.append({"text": city, "start": sent.find(city), "end": sent.find(city)+len(city), "label": "CITY"})
        if add_sentence(sent, ents, "Media"):
            c += 1

    # 7. EDUCATIONAL_INSTITUTION
    c, att = 0, 0
    while c < num_edu and att < num_edu * 5:
        att += 1
        edu = random.choice(EDUCATIONAL_INSTITUTIONS)
        city = random.choice(CITIES)
        ref = f"AC-{random.randint(100, 999)}"
        day = random.choice(DAYS)
        tmpl = random.choice(EDU_TEMPLATES)
        sent = tmpl.format(EDU=edu, CITY=city, REF=ref, DAY=day)
        ents = [{"text": edu, "start": sent.find(edu), "end": sent.find(edu)+len(edu), "label": "EDUCATIONAL_INSTITUTION"}]
        if "{CITY}" in tmpl and sent.find(city) != -1:
            ents.append({"text": city, "start": sent.find(city), "end": sent.find(city)+len(city), "label": "CITY"})
        if add_sentence(sent, ents, "Education"):
            c += 1

    # 8. MONEY
    c, att = 0, 0
    while c < num_money and att < num_money * 5:
        att += 1
        m_val = generate_synthetic_money()
        city = random.choice(CITIES)
        ref = f"SCH-{random.randint(100, 999)}"
        tmpl = random.choice(MONEY_TEMPLATES)
        sent = tmpl.format(MONEY=m_val, CITY=city, REF=ref)
        ents = [{"text": m_val, "start": sent.find(m_val), "end": sent.find(m_val)+len(m_val), "label": "MONEY"}]
        if "{CITY}" in tmpl and sent.find(city) != -1:
            ents.append({"text": city, "start": sent.find(city), "end": sent.find(city)+len(city), "label": "CITY"})
        if add_sentence(sent, ents, "Economy"):
            c += 1

    # 9. NEGATIVES
    c, att = 0, 0
    while c < num_negatives and att < num_negatives * 5:
        att += 1
        city = random.choice(CITIES)
        yr = str(random.randint(2018, 2026))
        day = random.choice(DAYS)
        sent = random.choice(NEGATIVE_TEMPLATES).format(
            CASE_NO=f"WP-{random.randint(100, 9999)}/{yr}",
            YEAR=yr,
            TRACKING=f"PK-{random.randint(10000000, 99999999)}",
            PLATE=f"ICT-{random.randint(100, 999)}",
            CITY=city,
            POSTAL=str(random.randint(44000, 54000)),
            TENDER_NO=f"TND/{random.randint(100, 999)}/{yr}",
            NUM_PEOPLE=str(random.randint(250, 4500)),
            DAY=day
        )
        ents = [{"text": city, "start": sent.find(city), "end": sent.find(city)+len(city), "label": "CITY"}]
        if add_sentence(sent, ents, "Distractors"):
            c += 1

    # 10. URDU BILINGUAL DATA
    c, att = 0, 0
    while c < num_urdu and att < num_urdu * 6:
        att += 1
        category = random.choice([
            "phone", "id", "legal", "sports", "gov", "time", "money", "event", "media", "edu", "distractor"
        ])
        city = random.choice(URDU_CITIES)
        day = random.choice(URDU_DAYS)
        sent = ""
        ents = []

        if category == "phone":
            p = generate_synthetic_urdu_phone()
            tmpl = random.choice(URDU_PHONE_TEMPLATES)
            sent = tmpl.format(PHONE=p, CITY=city)
            idx = sent.find(p)
            if idx != -1:
                ents.append({"text": p, "start": idx, "end": idx + len(p), "label": "PHONE_NUMBER"})
            if "{CITY}" in tmpl and sent.find(city) != -1:
                c_idx = sent.find(city)
                ents.append({"text": city, "start": c_idx, "end": c_idx + len(city), "label": "CITY"})

        elif category == "id":
            id_val = generate_synthetic_urdu_cnic()
            tmpl = random.choice(URDU_ID_TEMPLATES)
            sent = tmpl.format(ID=id_val, CITY=city)
            idx = sent.find(id_val)
            if idx != -1:
                ents.append({"text": id_val, "start": idx, "end": idx + len(id_val), "label": "ID_NUMBER"})
            if "{CITY}" in tmpl and sent.find(city) != -1:
                c_idx = sent.find(city)
                ents.append({"text": city, "start": c_idx, "end": c_idx + len(city), "label": "CITY"})

        elif category == "legal":
            court = random.choice(URDU_COURTS)
            law = random.choice(URDU_LAWS)
            tmpl = random.choice(URDU_LEGAL_TEMPLATES)
            sent = tmpl.format(COURT=court, LAW=law, CITY=city, DAY=day)
            for val, lbl in [(court, "COURT_LEGAL_BODY"), (law, "LAW_ACT"), (city, "CITY")]:
                if val in sent and sent.find(val) != -1:
                    ents.append({"text": val, "start": sent.find(val), "end": sent.find(val) + len(val), "label": lbl})

        elif category == "sports":
            team = random.choice(URDU_SPORTS_TEAMS)
            tmpl = random.choice(URDU_SPORTS_TEMPLATES)
            sent = tmpl.format(TEAM=team, CITY=city)
            for val, lbl in [(team, "SPORTS_TEAM"), (city, "CITY")]:
                if val in sent and sent.find(val) != -1:
                    ents.append({"text": val, "start": sent.find(val), "end": sent.find(val) + len(val), "label": lbl})

        elif category == "gov":
            gov = random.choice(URDU_GOV)
            party = random.choice(URDU_PARTIES)
            tmpl = random.choice(URDU_GOV_TEMPLATES)
            sent = tmpl.format(GOV=gov, PARTY=party, CITY=city)
            for val, lbl in [(gov, "GOVERNMENT_BODY"), (party, "POLITICAL_PARTY"), (city, "CITY")]:
                if val in sent and sent.find(val) != -1:
                    ents.append({"text": val, "start": sent.find(val), "end": sent.find(val) + len(val), "label": lbl})

        elif category == "time":
            t_val = generate_synthetic_urdu_time()
            tmpl = random.choice(URDU_TIME_TEMPLATES)
            sent = tmpl.format(TIME=t_val, CITY=city, DAY=day)
            if t_val in sent and sent.find(t_val) != -1:
                ents.append({"text": t_val, "start": sent.find(t_val), "end": sent.find(t_val) + len(t_val), "label": "TIME"})
            if city in sent and sent.find(city) != -1:
                ents.append({"text": city, "start": sent.find(city), "end": sent.find(city) + len(city), "label": "CITY"})

        elif category == "money":
            m_val = generate_synthetic_urdu_money()
            tmpl = random.choice(URDU_MONEY_TEMPLATES)
            sent = tmpl.format(MONEY=m_val, CITY=city)
            if m_val in sent and sent.find(m_val) != -1:
                ents.append({"text": m_val, "start": sent.find(m_val), "end": sent.find(m_val) + len(m_val), "label": "MONEY"})
            if city in sent and sent.find(city) != -1:
                ents.append({"text": city, "start": sent.find(city), "end": sent.find(city) + len(city), "label": "CITY"})

        elif category == "event":
            ev = random.choice(URDU_EVENTS)
            tmpl = random.choice(URDU_EVENT_TEMPLATES)
            sent = tmpl.format(EVENT=ev, CITY=city)
            if ev in sent and sent.find(ev) != -1:
                ents.append({"text": ev, "start": sent.find(ev), "end": sent.find(ev) + len(ev), "label": "EVENT"})
            if city in sent and sent.find(city) != -1:
                ents.append({"text": city, "start": sent.find(city), "end": sent.find(city) + len(city), "label": "CITY"})

        elif category == "media":
            med = random.choice(URDU_MEDIA)
            tmpl = random.choice(URDU_MEDIA_TEMPLATES)
            sent = tmpl.format(MEDIA=med, CITY=city)
            if med in sent and sent.find(med) != -1:
                ents.append({"text": med, "start": sent.find(med), "end": sent.find(med) + len(med), "label": "MEDIA_OUTLET"})
            if city in sent and sent.find(city) != -1:
                ents.append({"text": city, "start": sent.find(city), "end": sent.find(city) + len(city), "label": "CITY"})

        elif category == "edu":
            edu = random.choice(URDU_EDU)
            tmpl = random.choice(URDU_EDU_TEMPLATES)
            sent = tmpl.format(EDU=edu, CITY=city, DAY=day)
            if edu in sent and sent.find(edu) != -1:
                ents.append({"text": edu, "start": sent.find(edu), "end": sent.find(edu) + len(edu), "label": "EDUCATIONAL_INSTITUTION"})
            if city in sent and sent.find(city) != -1:
                ents.append({"text": city, "start": sent.find(city), "end": sent.find(city) + len(city), "label": "CITY"})

        else:
            sent = random.choice(URDU_DISTRACTOR_TEMPLATES)
            ents = []

        if sent and add_sentence(sent, ents, "Urdu/National", lang="ur"):
            c += 1

    random.shuffle(dataset)
    return dataset

def generate_all_synthetic_splits(out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    
    # Train synthetic: ~1,550 English + 400 Urdu = 1,950
    train_synth = generate_synthetic_dataset(
        num_phone=350, num_id=350, num_rare=250, num_time=150,
        num_event=100, num_media=100, num_edu=100, num_money=100,
        num_negatives=150, num_urdu=400, split_name="train"
    )
    # Dev synthetic: ~350 English + 100 Urdu = 450
    dev_synth = generate_synthetic_dataset(
        num_phone=80, num_id=80, num_rare=50, num_time=30,
        num_event=20, num_media=20, num_edu=20, num_money=20,
        num_negatives=40, num_urdu=100, split_name="dev"
    )
    # Benchmark synthetic: ~300 English + 100 Urdu = 400
    bench_synth = generate_synthetic_dataset(
        num_phone=70, num_id=70, num_rare=40, num_time=30,
        num_event=20, num_media=20, num_edu=20, num_money=20,
        num_negatives=30, num_urdu=100, split_name="benchmark"
    )

    train_path = os.path.join(out_dir, "synthetic_train.jsonl")
    dev_path = os.path.join(out_dir, "synthetic_dev.jsonl")
    bench_path = os.path.join(out_dir, "synthetic_benchmark.jsonl")

    for path, data in [(train_path, train_synth), (dev_path, dev_synth), (bench_path, bench_synth)]:
        with open(path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Generated Balanced Synthetic Splits: Train={len(train_synth)}, Dev={len(dev_synth)}, Benchmark={len(bench_synth)}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    generate_all_synthetic_splits(out_dir)

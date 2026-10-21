"""
Generator for v5 Augmented Dataset: 1,500 diverse contextual sentences.
"""

import os
import json
import random
from pathlib import Path

random.seed(42)

FIRST_NAMES = [
    "Shazia", "Mehwish", "Hira", "Sana", "Komal", "Maryam", "Saad", "Junaid",
    "Bilal", "Sadia", "Danish", "Omar", "Hamza", "Ali", "Usman", "Zain",
    "Ahmed", "Fatima", "Ayesha", "Zahra", "Tariq", "Asim", "Fahad", "Kamran",
    "Waqar", "Noman", "Farhan", "Bakhtawar", "Zeeshan", "Zubair", "Rashid",
    "Adnan", "Salman", "Rehan", "Arsalan", "Ahsan", "Umair", "Waleed", "Atif"
]

LAST_NAMES = [
    "Baig", "Ansari", "Javed", "Rehman", "Rahman", "Ahmed", "Ahmad", "Farooqui",
    "Farooq", "Siddiqui", "Ghani", "Malik", "Butt", "Shaikh", "Sheikh", "Khan",
    "Chaudhry", "Choudhary", "Qureshi", "Raza", "Shah", "Memon", "Abbasi",
    "Khattak", "Afridi", "Bugti", "Mengal", "Baloch", "Mirza", "Cheema", "Tarar",
    "Gilani", "Lund", "Khawaja", "Wattoo", "Leghari", "Mazari"
]

SPORTS_TEAMS = [
    "Pakistan", "India", "Australia", "England", "South Africa", "New Zealand",
    "Sri Lanka", "Bangladesh", "Afghanistan", "West Indies", "Lahore Qalandars",
    "Karachi Kings", "Islamabad United", "Peshawar Zalmi", "Quetta Gladiators",
    "Multan Sultans", "Karachi Whites", "Lahore Blues", "Sialkot Stallions"
]

CITIES = [
    "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Quetta",
    "Multan", "Faisalabad", "Sialkot", "Hyderabad", "Sukkur", "Abbottabad",
    "Bahawalpur", "Sargodha", "Mirpur", "Swat", "Gwadar", "Larkana"
]

LANDMARKS = [
    "Gaddafi Stadium", "National Stadium", "Iqbal Stadium", "Islamabad Expo Centre",
    "Lahore Expo Centre", "Karachi Expo Centre", "Clifton Beach", "Frere Hall",
    "Faisal Mosque", "Badshahi Mosque", "Minar-e-Pakistan", "Mazar-e-Quaid",
    "Jinnah International Airport", "Allama Iqbal International Airport",
    "Karakoram Highway", "M-2 Motorway"
]

ORGS = [
    "Fauji Foundation", "Systems Limited", "Careem", "Bykea", "Daraz",
    "Engro Corporation", "Lucky Cement", "Habib Bank Limited", "Meezan Bank",
    "NetSol", "10Pearls", "Telenor Pakistan", "Jazz Pakistan", "Zong Pakistan",
    "K-Electric", "PTCL", "Edhi Foundation", "Saylani Welfare Trust"
]

GOV_BODIES = [
    "Pakistan Meteorological Department", "Higher Education Commission",
    "Capital Development Authority", "Government of Sindh", "Government of Punjab",
    "Khyber Pakhtunkhwa government", "Balochistan government", "State Bank of Pakistan",
    "Federal Board of Revenue", "National Accountability Bureau", "FIA", "NADRA"
]

COURTS = [
    "Supreme Court of Pakistan", "Lahore High Court", "Sindh High Court",
    "Islamabad High Court", "Peshawar High Court", "Balochistan High Court",
    "Anti-Terrorism Court"
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def get_person():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def get_phone():
    fmt = random.choice(["bracket", "hyphen", "plus92"])
    if fmt == "bracket":
        code = random.choice(["021", "042", "051", "041", "091"])
        return f"({code}) {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
    elif fmt == "hyphen":
        code = random.choice(["0300", "0321", "0333", "0345", "0312"])
        return f"{code}-{random.randint(1000000, 9999999)}"
    else:
        code = random.choice(["300", "321", "333", "345"])
        return f"+92 {code} {random.randint(1000000, 9999999)}"

def get_cnic():
    p1 = random.randint(10000, 79999)
    p2 = random.randint(1000000, 9999999)
    p3 = random.randint(1, 9)
    return f"{p1}-{p2}-{p3}"

def get_money():
    amt = random.randint(5, 950)
    unit = random.choice(["crore", "lakh", "million", "billion"])
    return f"Rs. {amt} {unit}"

def t1():
    p = get_person()
    c = random.choice(COURTS)
    d = random.choice(DAYS)
    text = f"The constitutional petition was filed by {p} in the {c} on {d}."
    return text, [(p, "PERSON"), (c, "COURT_LEGAL_BODY"), (d, "DATE")]

def t2():
    p1 = get_person()
    p2 = get_person()
    c = random.choice(COURTS)
    text = f"The accused, {p1}, son of {p2}, was granted bail by the {c}."
    return text, [(p1, "PERSON"), (p2, "PERSON"), (c, "COURT_LEGAL_BODY")]

def t3():
    t1_team = random.choice(SPORTS_TEAMS)
    t2_team = random.choice([t for t in SPORTS_TEAMS if t != t1_team])
    runs = random.randint(10, 250)
    l = random.choice(LANDMARKS)
    d = random.choice(DAYS)
    text = f"{t1_team} defeated {t2_team} by {runs} runs at {l} on {d}."
    return text, [(t1_team, "SPORTS_TEAM"), (t2_team, "SPORTS_TEAM"), (l, "LANDMARK_FACILITY"), (d, "DATE")]

def t4():
    p = get_person()
    o = random.choice(ORGS)
    city = random.choice(CITIES)
    d = random.choice(DAYS)
    text = f"Dear {p}, your job interview at {o} in {city} is scheduled for {d}."
    return text, [(p, "PERSON"), (o, "ORGANIZATION"), (city, "CITY"), (d, "DATE")]

def t5():
    p = get_person()
    ph = get_phone()
    o = random.choice(ORGS)
    text = f"Please contact {p} at {ph} regarding admissions at {o}."
    return text, [(p, "PERSON"), (ph, "PHONE_NUMBER"), (o, "ORGANIZATION")]

def t6():
    p = get_person()
    o = random.choice(ORGS)
    city = random.choice(CITIES)
    text = f"{p} was appointed president of {o} in {city}."
    return text, [(p, "PERSON"), (o, "ORGANIZATION"), (city, "CITY")]

def t7():
    p = get_person()
    o = random.choice(ORGS)
    m = random.choice(MONTHS)
    text = f"{p} resigned from {o} ahead of {m}."
    return text, [(p, "PERSON"), (o, "ORGANIZATION"), (m, "DATE")]

def t8():
    p = get_person()
    cnic = get_cnic()
    city = random.choice(CITIES)
    text = f"Voter ID check: {p}, {cnic}, registered in {city}."
    return text, [(p, "PERSON"), (cnic, "ID_NUMBER"), (city, "CITY")]

def t9():
    p = get_person()
    t = random.choice(SPORTS_TEAMS)
    w = random.randint(3, 7)
    l = random.choice(LANDMARKS)
    text = f"{p} of {t} took {w} wickets at {l}."
    return text, [(p, "PERSON"), (t, "SPORTS_TEAM"), (l, "LANDMARK_FACILITY")]

def t10():
    gov = random.choice(GOV_BODIES)
    m = get_money()
    city = random.choice(CITIES)
    text = f"{gov} has allocated {m} for development projects in {city}."
    return text, [(gov, "GOVERNMENT_BODY"), (m, "MONEY"), (city, "CITY")]

def t11():
    l = random.choice(LANDMARKS)
    city = random.choice(CITIES)
    d = random.choice(DAYS)
    text = f"Traffic near {l} in {city} was diverted on {d}."
    return text, [(l, "LANDMARK_FACILITY"), (city, "CITY"), (d, "DATE")]

def t12():
    o = random.choice(ORGS)
    pct = f"{random.randint(5, 35)}%"
    m = random.choice(MONTHS)
    text = f"Shares of {o} surged {pct} in {m}."
    return text, [(o, "ORGANIZATION"), (pct, "PERCENT"), (m, "DATE")]

TEMPLATES = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12]

def build_annotated_sentence(fn):
    text, entities_spec = fn()
    entities = []
    for span_text, label in entities_spec:
        idx = text.find(span_text)
        if idx != -1:
            entities.append({
                "start": idx,
                "end": idx + len(span_text),
                "label": label,
                "text": span_text
            })
    entities.sort(key=lambda x: x["start"])
    return {"text": text, "entities": entities}

if __name__ == "__main__":
    out_dir = Path("v5")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "train_augmented_1500.jsonl"
    
    samples = [build_annotated_sentence(random.choice(TEMPLATES)) for _ in range(1500)]
    with open(out_path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
            
    print(f"Generated {len(samples)} valid contextual samples -> {out_path}")

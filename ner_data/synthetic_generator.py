"""
Synthetic PHONE_NUMBER and ID_NUMBER sentence generator.
Strict adherence to Rule 3: 100% fake random digits, 0% real citizen PII.
Generates 600+ varied sentences across 30+ templates with exact entity character offsets.
"""

import os
import random
import json
from typing import List, Dict, Any

random.seed(42)

MOBILE_CODES = ["300", "301", "302", "303", "304", "305", "306", "307", "308", "309",
                "310", "311", "312", "313", "314", "315", "316", "317", "318",
                "320", "321", "322", "323", "324", "325",
                "330", "331", "332", "333", "334", "335", "336", "337",
                "340", "341", "342", "343", "344", "345", "346", "347"]
LANDLINE_CODES = ["021", "042", "051", "091", "081", "041", "061", "022", "052", "055"]

PROVINCE_CODES = ["1", "2", "3", "4", "5", "6", "7"]

def generate_fake_phone() -> str:
    fmt = random.choice(["plus92_spaced", "plus92_hyphen", "local_hyphen", "local_spaced", "landline"])
    if fmt == "plus92_spaced":
        code = random.choice(MOBILE_CODES)
        p1 = f"{random.randint(100, 999)}"
        p2 = f"{random.randint(1000, 9999)}"
        return f"+92 {code} {p1}{p2}"
    elif fmt == "plus92_hyphen":
        code = random.choice(MOBILE_CODES)
        p1 = f"{random.randint(1000, 9999)}"
        p2 = f"{random.randint(100, 999)}"
        return f"+92-{code}-{p1}{p2}"
    elif fmt == "local_hyphen":
        code = random.choice(MOBILE_CODES)
        rest = f"{random.randint(1000000, 9999999)}"
        return f"0{code}-{rest}"
    elif fmt == "local_spaced":
        code = random.choice(MOBILE_CODES)
        rest = f"{random.randint(1000000, 9999999)}"
        return f"0{code} {rest}"
    else:
        code = random.choice(LANDLINE_CODES)
        rest = f"{random.randint(1000000, 9999999)}"
        return f"{code}-{rest}"

def generate_fake_cnic() -> str:
    prov = random.choice(PROVINCE_CODES)
    div = f"{random.randint(100, 999)}"
    seq = f"{random.randint(1000000, 9999999)}"
    chk = f"{random.randint(1, 9)}"
    return f"{prov}{div}1-{seq}-{chk}"

# 30+ Varied Real-world Pakistani administrative templates
PHONE_TEMPLATES = [
    "For customer assistance and complaint filing, citizens can contact helpline {phone}.",
    "In case of any emergency at the venue, please call the control room on {phone}.",
    "Candidates facing technical difficulties should immediately reach out to {phone} for guidance.",
    "The spokesperson announced that inquiries regarding admissions can be made at {phone}.",
    "For urgent verification and passport status updates, ring {phone} during office hours.",
    "Interested bidders are requested to confirm their tender participation via {phone}.",
    "The helpline service is active 24/7; callers may dial {phone} for assistance.",
    "Members of the general public can register their grievances by calling {phone} directly.",
    "For media inquiries and official press credentials, contact the secretariat at {phone}.",
    "Please send your confirmation code or contact our support representative at {phone}.",
    "The dispatch center confirmed that callers can reach the traffic rescue squad at {phone}.",
    "For further information on the investment conference, dial {phone} between 9 AM and 5 PM.",
    "Taxpayers seeking guidance on filing annual returns can call the helpline {phone}.",
    "Emergency medical response services are accessible round the clock at {phone}.",
    "The election monitoring cell set up by the district administration is reachable at {phone}."
]

CNIC_TEMPLATES = [
    "The designated applicant with CNIC {cnic} submitted the required documentation today.",
    "Verification of the nominee holding identity card {cnic} was concluded by the returning officer.",
    "Beneficiaries registered under national identity card {cnic} are entitled to collect their subsidy.",
    "The official report listed candidate CNIC: {cnic} as eligible for the recruitment examination.",
    "Please ensure that the account holder details match the official CNIC {cnic} on file.",
    "NADRA confirmed the issuance of the smart card for citizen CNIC {cnic} at the regional center.",
    "The complaint was lodged against the individual identified by identity card number {cnic}.",
    "The bank requested the customer with registered CNIC: {cnic} to update biometric verification.",
    "Passport authorities notified the citizen carrying CNIC {cnic} regarding collection.",
    "The court record specifies the CNIC of the guarantor as {cnic} in the proceedings.",
    "Land revenue records registered the property deed in the name of holder CNIC {cnic}.",
    "The electoral roll confirmed the registration of voter holding CNIC: {cnic} in NA-128.",
    "Security clearance for the visitor bearing CNIC {cnic} was issued at the main secretariat.",
    "The scholarship award was granted to the undergraduate student with CNIC {cnic}.",
    "The applicant submitted a certified photocopy of CNIC: {cnic} along with the application form."
]

COMBINED_TEMPLATES = [
    "The applicant holding CNIC {cnic} can be reached at emergency contact {phone}.",
    "For inquiries regarding verification of CNIC {cnic}, please contact the support desk at {phone}.",
    "Citizen with national identity card {cnic} registered a formal complaint via phone number {phone}.",
    "The registered vendor with CNIC {cnic} was notified of payment processing through contact {phone}.",
    "Please confirm the details of account holder CNIC: {cnic} by calling the branch manager on {phone}."
]

def generate_synthetic_dataset(output_path: str, count: int = 650):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    records: List[Dict[str, Any]] = []

    # Distribution: ~260 phone, ~260 cnic, ~130 combined
    for i in range(count):
        sent_id = f"synth_{i+1:04d}"
        if i < 260:
            phone = generate_fake_phone()
            tpl = random.choice(PHONE_TEMPLATES)
            start = tpl.find("{phone}")
            text = tpl.replace("{phone}", phone)
            entities = [{"start": start, "end": start + len(phone), "label": "PHONE_NUMBER", "mention": phone}]
        elif i < 520:
            cnic = generate_fake_cnic()
            tpl = random.choice(CNIC_TEMPLATES)
            start = tpl.find("{cnic}")
            text = tpl.replace("{cnic}", cnic)
            entities = [{"start": start, "end": start + len(cnic), "label": "ID_NUMBER", "mention": cnic}]
        else:
            phone = generate_fake_phone()
            cnic = generate_fake_cnic()
            tpl = random.choice(COMBINED_TEMPLATES)
            
            # Place CNIC first, then phone
            t_half = tpl.replace("{cnic}", cnic)
            start_cnic = tpl.find("{cnic}")
            end_cnic = start_cnic + len(cnic)
            
            start_phone = t_half.find("{phone}")
            text = t_half.replace("{phone}", phone)
            end_phone = start_phone + len(phone)
            
            entities = [
                {"start": start_cnic, "end": end_cnic, "label": "ID_NUMBER", "mention": cnic},
                {"start": start_phone, "end": end_phone, "label": "PHONE_NUMBER", "mention": phone}
            ]

        records.append({
            "id": sent_id,
            "text": text,
            "language": "en",
            "source_domain": "synthetic_generator",
            "source_category": "Synthetic/Rule3_PII",
            "article_url": "synthetic://rule3_pii_privacy_safe",
            "article_id": f"art_synth_{(i // 10) + 1}",
            "date": "2026-10-20",
            "synthetic": True,
            "entities": entities
        })

    with open(output_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Generated {len(records)} synthetic PII sentences saved to {output_path}")

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "synthetic", "phone_id_sentences.jsonl")
    generate_synthetic_dataset(out_file, 650)

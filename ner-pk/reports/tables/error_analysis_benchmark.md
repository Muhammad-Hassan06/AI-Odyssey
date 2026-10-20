# Error Analysis & Diagnostic Log (BENCHMARK Split)

## Boundary Mismatches (27 occurrences)

- **Issue:** Boundary offset mismatch: gold (132:142) vs pred (132:152)
  - *Sentence:* "It also includes facilities to accommodate two double-decker Airbus A380s, 15 remote bays and 3 remote bays for Air cargo.[99]

The Rawalpindi-Islamabad Metrobus is a 83.6 km (51.9 mi) bus rapid transit system operating in the Islamabad-Rawalpindi metropolitan area."

- **Issue:** Boundary offset mismatch: gold (143:152) vs pred (132:152)
  - *Sentence:* "It also includes facilities to accommodate two double-decker Airbus A380s, 15 remote bays and 3 remote bays for Air cargo.[99]

The Rawalpindi-Islamabad Metrobus is a 83.6 km (51.9 mi) bus rapid transit system operating in the Islamabad-Rawalpindi metropolitan area."

- **Issue:** Boundary offset mismatch: gold (227:236) vs pred (227:247)
  - *Sentence:* "It also includes facilities to accommodate two double-decker Airbus A380s, 15 remote bays and 3 remote bays for Air cargo.[99]

The Rawalpindi-Islamabad Metrobus is a 83.6 km (51.9 mi) bus rapid transit system operating in the Islamabad-Rawalpindi metropolitan area."

- **Issue:** Boundary offset mismatch: gold (237:247) vs pred (227:247)
  - *Sentence:* "It also includes facilities to accommodate two double-decker Airbus A380s, 15 remote bays and 3 remote bays for Air cargo.[99]

The Rawalpindi-Islamabad Metrobus is a 83.6 km (51.9 mi) bus rapid transit system operating in the Islamabad-Rawalpindi metropolitan area."

- **Issue:** Boundary offset mismatch: gold (148:153) vs pred (148:162)
  - *Sentence:* "Pakistan's motorway network links Peshawar to Faisalabad by the M-4 Motorway, while a new motorway network to Karachi is being built as part of the China Pakistan Economic Corridor."

- **Issue:** Boundary offset mismatch: gold (154:162) vs pred (148:162)
  - *Sentence:* "Pakistan's motorway network links Peshawar to Faisalabad by the M-4 Motorway, while a new motorway network to Karachi is being built as part of the China Pakistan Economic Corridor."

- **Issue:** Boundary offset mismatch: gold (105:110) vs pred (105:119)
  - *Sentence:* "The M-9 motorway is part of a larger countrywide motorways network, many of which were built through the China Pakistan Economic Corridor Project."

- **Issue:** Boundary offset mismatch: gold (111:119) vs pred (105:119)
  - *Sentence:* "The M-9 motorway is part of a larger countrywide motorways network, many of which were built through the China Pakistan Economic Corridor Project."

## Type Confusions (17 occurrences)

- **Issue:** Type confusion: gold 'COUNTRY' predicted as 'GOVERNMENT_BODY'
  - *Sentence:* "The Pakistan Electronic Media Regulatory Authority (PEMRA) has been used to silence the broadcast media by either suspending licenses or by simply threatening to do so.[3] Media coverage of abuses by both the Pakistan Armed Forces and militant groups is hindered by an ongoing climate of fear."

- **Issue:** Type confusion: gold 'COUNTRY' predicted as 'GOVERNMENT_BODY'
  - *Sentence:* "Security in Gilgit-Baltistan is provided by the Gilgit-Baltistan Police, the Gilgit Baltistan Scouts (a paramilitary force), and the Northern Light Infantry (part of the Pakistan Army)."

- **Issue:** Type confusion: gold 'COUNTRY' predicted as 'GOVERNMENT_BODY'
  - *Sentence:* "To the east of the historic core is the area known as Defence, an expansive upscale suburb developed and administered by the Pakistan Army."

- **Issue:** Type confusion: gold 'EVENT' predicted as 'COUNTRY'
  - *Sentence:* "پاکستان سپر لیگ کے پرامن انعقاد کے لیے کوئٹہ میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

- **Issue:** Type confusion: gold 'CITY' predicted as 'SPORTS_TEAM'
  - *Sentence:* "ملتان سلطانز کے کپتان نے پریس کانفرنس کرتے ہوئے آئندہ میچ کی حکمت عملی پر بات کی۔"

- **Issue:** Type confusion: gold 'EVENT' predicted as 'COUNTRY'
  - *Sentence:* "پاکستان سپر لیگ کی رنگارنگ افتتاحی تقریب راولپنڈی میں جوش و خروش سے منائی گئی۔"

- **Issue:** Type confusion: gold 'CITY' predicted as 'COURT_LEGAL_BODY'
  - *Sentence:* "لاہور ہائی کورٹ نے 26ویں آئینی ترمیم کے تحت دائر آئینی درخواست کی سماعت ہفتہ تک ملتوی کر دی۔"

- **Issue:** Type confusion: gold 'EVENT' predicted as 'COUNTRY'
  - *Sentence:* "یوم پاکستان کی رنگارنگ افتتاحی تقریب ملتان میں جوش و خروش سے منائی گئی۔"

## False Negatives (18 occurrences)

- **Issue:** Missed entity: '26ویں آئینی ترمیم' [LAW_ACT]
  - *Sentence:* "لاہور ہائی کورٹ نے 26ویں آئینی ترمیم کے تحت دائر آئینی درخواست کی سماعت ہفتہ تک ملتوی کر دی۔"

- **Issue:** Missed entity: 'یوم دفاع' [EVENT]
  - *Sentence:* "یوم دفاع کے پرامن انعقاد کے لیے حیدرآباد میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

- **Issue:** Missed entity: 'یوم آزادی' [EVENT]
  - *Sentence:* "یوم آزادی کے پرامن انعقاد کے لیے کراچی میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

- **Issue:** Missed entity: 'Multan' [CITY]
  - *Sentence:* "The tender quotation reference was TND/628/2025 issued in 2025."

- **Issue:** Missed entity: 'وفاقی بجٹ' [EVENT]
  - *Sentence:* "وفاقی بجٹ کے پرامن انعقاد کے لیے لاہور میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

- **Issue:** Missed entity: 'Lahore' [CITY]
  - *Sentence:* "The case reference was registered under file number WP-924/2024 in 2024."

- **Issue:** Missed entity: 'Faisalabad' [CITY]
  - *Sentence:* "The tender quotation reference was TND/820/2023 issued in 2023."

- **Issue:** Missed entity: 'Lahore' [CITY]
  - *Sentence:* "The case reference was registered under file number WP-9275/2020 in 2020."

## False Positives (118 occurrences)

- **Issue:** Spurious entity: 'high court' [COURT_LEGAL_BODY]
  - *Sentence:* "Established as a high court on 21 March 1882, it is based in Lahore, which is its principal seat; alongside its secondary benches based in Rawalpindi, Multan, and Bahawalpur.[1]

A proposal was sent by lawyers to set up new high court benches in Faisalabad, Sialkot, D.G.Khan and Gujranwala divisions but full court of Lahore High Court turned down this request.[2]

In 1849, the East India Company defeated the Sikh Empire and assumed control of administration within the Punjab."

- **Issue:** Spurious entity: 'high court' [COURT_LEGAL_BODY]
  - *Sentence:* "Established as a high court on 21 March 1882, it is based in Lahore, which is its principal seat; alongside its secondary benches based in Rawalpindi, Multan, and Bahawalpur.[1]

A proposal was sent by lawyers to set up new high court benches in Faisalabad, Sialkot, D.G.Khan and Gujranwala divisions but full court of Lahore High Court turned down this request.[2]

In 1849, the East India Company defeated the Sikh Empire and assumed control of administration within the Punjab."

- **Issue:** Spurious entity: 'High Court' [COURT_LEGAL_BODY]
  - *Sentence:* "An age limit of 60 years was set for High Court Judges.[4]

By virtue of the Government of India (High Court Judges) Order, 1937, a maximum number of Judges for the various High Courts in India was fixed."

- **Issue:** Spurious entity: 'High Court' [COURT_LEGAL_BODY]
  - *Sentence:* "An age limit of 60 years was set for High Court Judges.[4]

By virtue of the Government of India (High Court Judges) Order, 1937, a maximum number of Judges for the various High Courts in India was fixed."

- **Issue:** Spurious entity: 'High Court' [COURT_LEGAL_BODY]
  - *Sentence:* "For the Lahore High Court the maximum number was fixed at 15.[4]

The West Pakistan High Court

On 30 September 1955, the Constituent Assembly of Pakistan established the province of West Pakistan, and gave the Governor-General the power to establish the West Pakistan High Court, which was established in 1956."

- **Issue:** Spurious entity: 'High Court' [COURT_LEGAL_BODY]
  - *Sentence:* "For the Lahore High Court the maximum number was fixed at 15.[4]

The West Pakistan High Court

On 30 September 1955, the Constituent Assembly of Pakistan established the province of West Pakistan, and gave the Governor-General the power to establish the West Pakistan High Court, which was established in 1956."

- **Issue:** Spurious entity: 'High Court' [COURT_LEGAL_BODY]
  - *Sentence:* "Judges from the Chief Court of Sind and the Judicial Commissioners Court at Peshawar became judges at the West Pakistan High Court.[8]

Creation Of Divisional Benches

On 1 January 1981, it was ordered that the Lahore High Court would create benches at Bahawalpur, Multan and Rawalpindi."

- **Issue:** Spurious entity: 'Gilgit' [CITY]
  - *Sentence:* "Gilgit-Baltistan is named after the two former agencies, Gilgit and Baltistan, which were merged in 1972 to form Northern Areas."


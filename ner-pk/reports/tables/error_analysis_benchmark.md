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

## Type Confusions (14 occurrences)

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

- **Issue:** Type confusion: gold 'GOVERNMENT_BODY' predicted as 'COUNTRY'
  - *Sentence:* "سٹیٹ بینک آف پاکستان کی ہدایت پر کراچی کی ضلعی انتظامیہ نے آپریشن کا آغاز کیا۔"

- **Issue:** Type confusion: gold 'EVENT' predicted as 'COUNTRY'
  - *Sentence:* "یوم پاکستان کے پرامن انعقاد کے لیے حیدرآباد میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

- **Issue:** Type confusion: gold 'EVENT' predicted as 'COUNTRY'
  - *Sentence:* "پاکستان سپر لیگ کے پرامن انعقاد کے لیے راولپنڈی میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

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

## False Positives (111 occurrences)

- **Issue:** Spurious entity: 'Gilgit' [CITY]
  - *Sentence:* "Gilgit-Baltistan is named after the two former agencies, Gilgit and Baltistan, which were merged in 1972 to form Northern Areas."

- **Issue:** Spurious entity: 'Gilgit' [CITY]
  - *Sentence:* "Between 399 and 414, the Chinese Buddhist pilgrim Faxian visited Gilgit-Baltistan.[30] In the 6th century Somana Palola (greater Gilgit-Chilas) was ruled by an unknown king."

- **Issue:** Spurious entity: 'Skardu' [CITY]
  - *Sentence:* "The resentment and help of rajas deposed by them aided Dogra dynasty in conquering much of Gilgit-Baltistan in the succeeding decades.[50]

In November 1839, the Dogra commander Zorawar Singh, whose allegiance was to Gulab Singh, invaded Baltistan.[51] By 1840 he had conquered Skardu and captured Ahmad Shah."

- **Issue:** Spurious entity: 'Gilgit' [CITY]
  - *Sentence:* "It was not until his death in 1860 that Dogras finally managed to subdue Gilgit.[56]

After the defeat of the Sikhs in the First Anglo-Sikh War, the Lahore court had to cede Kashmir Valley and the neighbouring Himalayan areas to the British in the treaty of Lahore, who in turn sold these areas to Gulab Singh for 7.5 million Nanakshahi rupees after the signing of Treaty of Amritsar, and also confirmed him on his conquests in Baltistan and Ladakh."

- **Issue:** Spurious entity: 'Gilgit' [CITY]
  - *Sentence:* "The population in Gilgit perceived itself as ethnically different from Kashmiris and disliked being ruled by the Kashmir state.[57] The region remained with the princely state, with temporary leases of some areas assigned to the British, until 1 November 1947."

- **Issue:** Spurious entity: 'Gilgit' [CITY]
  - *Sentence:* "Gilgit's population did not favour the State's accession to India.[61] The Muslims of the frontier ilaqas (Gilgit and the adjoining hill states) had wanted to join Pakistan.[62] Sensing their discontent, Major William Brown, the Maharaja's commander of the Gilgit Scouts, mutinied on 1 November 1947, directing his Subedar-Major Babar Khan to arrest the governor Ghansara Singh."

- **Issue:** Spurious entity: 'Gilgit' [CITY]
  - *Sentence:* "Gilgit's population did not favour the State's accession to India.[61] The Muslims of the frontier ilaqas (Gilgit and the adjoining hill states) had wanted to join Pakistan.[62] Sensing their discontent, Major William Brown, the Maharaja's commander of the Gilgit Scouts, mutinied on 1 November 1947, directing his Subedar-Major Babar Khan to arrest the governor Ghansara Singh."

- **Issue:** Spurious entity: 'Gilgit' [CITY]
  - *Sentence:* "Gilgit's population did not favour the State's accession to India.[61] The Muslims of the frontier ilaqas (Gilgit and the adjoining hill states) had wanted to join Pakistan.[62] Sensing their discontent, Major William Brown, the Maharaja's commander of the Gilgit Scouts, mutinied on 1 November 1947, directing his Subedar-Major Babar Khan to arrest the governor Ghansara Singh."


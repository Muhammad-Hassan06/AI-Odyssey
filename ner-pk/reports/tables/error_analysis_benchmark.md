# Error Analysis & Diagnostic Log (BENCHMARK Split)

## Boundary Mismatches (13 occurrences)

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

## Type Confusions (3 occurrences)

- **Issue:** Type confusion: gold 'COUNTRY' predicted as 'GOVERNMENT_BODY'
  - *Sentence:* "The Pakistan Electronic Media Regulatory Authority (PEMRA) has been used to silence the broadcast media by either suspending licenses or by simply threatening to do so.[3] Media coverage of abuses by both the Pakistan Armed Forces and militant groups is hindered by an ongoing climate of fear."

- **Issue:** Type confusion: gold 'COUNTRY' predicted as 'GOVERNMENT_BODY'
  - *Sentence:* "Security in Gilgit-Baltistan is provided by the Gilgit-Baltistan Police, the Gilgit Baltistan Scouts (a paramilitary force), and the Northern Light Infantry (part of the Pakistan Army)."

- **Issue:** Type confusion: gold 'COUNTRY' predicted as 'GOVERNMENT_BODY'
  - *Sentence:* "To the east of the historic core is the area known as Defence, an expansive upscale suburb developed and administered by the Pakistan Army."

## False Negatives (12 occurrences)

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The tender quotation reference was TND/628/2025 issued in 2025."

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The case reference was registered under file number WP-924/2024 in 2024."

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The tender quotation reference was TND/820/2023 issued in 2023."

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The case reference was registered under file number WP-9275/2020 in 2020."

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The tender quotation reference was TND/975/2024 issued in 2024."

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The case reference was registered under file number WP-5986/2020 in 2020."

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The case reference was registered under file number WP-9087/2018 in 2018."

- **Issue:** Missed entity: 'نمل یونیورسٹی' [EDUCATIONAL_INSTITUTION]
  - *Sentence:* "نمل یونیورسٹی کے ہونہار طلبہ نے کوئٹہ میں جدید ٹیکنالوجی پر مبنی پروجیکٹ پیش کیا۔"

## False Positives (165 occurrences)

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


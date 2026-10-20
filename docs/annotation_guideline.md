# Pakistani-Context Named Entity Recognition (NER) Annotation Guideline
**TechFest NER Challenge: Dory's Data Dive (Round 2)**  
*Document Version:* 2.0 | *Standard:* Flat IOB2 Span Labeling | *Scope:* English & Urdu Text

---

## 1. Core Principles & Boundary Standards

1. **Strict Flat Annotation (No Nesting):** Entities must not overlap or nest. Each character in the text belongs to at most one entity span.
2. **Longest Meaningful Span Rule:** When an entity span contains an embedded sub-entity, always select the longest span representing the outer, most specific entity.
   - *Example:* `[Karachi Kings]_SPORTS_TEAM` (NOT `[Karachi]_CITY` inside `Kings`).
   - *Example:* `[Lahore High Court]_COURT_LEGAL_BODY` (NOT `[Lahore]_CITY`).
   - *Example:* `[Allama Iqbal International Airport]_LANDMARK_FACILITY` (NOT `[Allama Iqbal]_PERSON` or `[International Airport]`).
3. **Leading Articles ("The", "A", "An"):** Exclude leading articles unless they are an intrinsic, capitalized part of the official brand or legal entity title.
   - *Correct:* `"the [Supreme Court of Pakistan]_COURT_LEGAL_BODY"`
   - *Correct:* `"[The News International]_MEDIA_OUTLET"` (official publication title)
4. **Titles and Honorifics:** Exclude all professional, political, military, judicial, or religious titles and honorifics from `PERSON` spans.
   - *Excluded prefixes:* *Mr.*, *Mrs.*, *Dr.*, *Justice*, *Chief Justice*, *Prime Minister*, *President*, *General*, *Senator*, *Maulana*, *Syed*, *Chaudhry*, *Mian*, *Sardar*, *Pir*.
   - *Excluded suffixes:* *Sahib*, *R.A.*, *Advocate Supreme Court*.
   - *Example:* `"Prime Minister [Shehbaz Sharif]_PERSON met with Chief Justice [Yahya Afridi]_PERSON."`
5. **Punctuation & Possessives:**
   - Exclude trailing punctuation marks (`,`, `.`, `;`, `:`) unless part of an abbreviation (e.g., `[U.S.]_COUNTRY`, `[Rs.]_MONEY`).
   - Exclude possessive clitics (`'s`, `’s`, `s'`).
   - *Example:* `"[LUMS]_EDUCATIONAL_INSTITUTION's campus"` (NOT `LUMS's`).
6. **Range Expressions:** Numeric and temporal ranges should be tagged as a single composite span when connected by hyphens or range prepositions.
   - *Example:* `"[2024-2025]_DATE"`, `"[10:00 AM to 1:00 PM]_TIME"`, `"[Rs 50-60 million]_MONEY"`.

---

## 2. Disambiguation Rules for the 20 Entity Categories

### A. Institutional Disambiguation: `ORGANIZATION` vs `GOVERNMENT_BODY` vs `COURT_LEGAL_BODY`
* **`COURT_LEGAL_BODY`:** Any constitutional court, high court, district judiciary, appellate tribunal, or judicial commission.
  - *Positive:* `Supreme Court of Pakistan`, `Lahore High Court`, `Sindh High Court`, `Federal Shariat Court`, `Election Tribunal`, `National Accountability Court`.
  - *Negative:* `Ministry of Law` (`GOVERNMENT_BODY`), `Law and Justice Commission` (`GOVERNMENT_BODY`).
* **`GOVERNMENT_BODY`:** Executive state ministries, public statutory regulators, armed services, civil services, municipal authorities, and government commissions.
  - *Positive:* `Federal Board of Revenue` (`FBR`), `State Bank of Pakistan` (`SBP`), `Ministry of Finance`, `National Database and Registration Authority` (`NADRA`), `Pakistan Telecommunication Authority` (`PTA`), `Election Commission of Pakistan` (`ECP`), `Pakistan Army`.
  - *Negative:* Commercial banks or state-owned enterprises that operate commercially (`ORGANIZATION`).
* **`ORGANIZATION`:** Commercial corporations, state-owned business enterprises (SOEs), NGOs, charities, international bodies, and trade unions.
  - *Positive:* `Habib Bank Limited` (`HBL`), `Engro Corporation`, `Pakistan International Airlines` (`PIA`), `Pakistan Railways`, `OGDCL`, `Edhi Foundation`, `United Nations`, `IMF`, `World Bank`.
  - *Negative:* `State Bank of Pakistan` (`GOVERNMENT_BODY`), `Ministry of Railways` (`GOVERNMENT_BODY`).

### B. Geographic Disambiguation: `CITY` vs `LANDMARK_FACILITY` vs `PROVINCE_REGION`
* **`CITY`:** Inhabited urban settlements, municipalities, towns, tehsils, and union councils.
  - *Positive:* `Karachi`, `Lahore`, `Islamabad`, `Faisalabad`, `Peshawar`, `Quetta`, `Gwadar`, `Mirpur`.
  - *Negative:* `Karachi Port` (`LANDMARK_FACILITY`), `Sindh` (`PROVINCE_REGION`).
* **`PROVINCE_REGION`:** Constitutional provinces, administrative divisions, autonomous regions, valleys, and trans-provincial geographic regions.
  - *Positive:* `Punjab`, `Sindh`, `Khyber Pakhtunkhwa` (`KP`), `Balochistan`, `Gilgit-Baltistan` (`GB`), `Azad Jammu and Kashmir` (`AJK`), `Potohar`, `Swat Valley`, `Thar Desert`.
  - *Negative:* `Lahore` (`CITY`), `Pakistan` (`COUNTRY`).
* **`LANDMARK_FACILITY`:** Built infrastructure, public utilities, transit terminals, airports, seaports, sports stadiums, dams, motorways, hospitals, and national monuments.
  - *Positive:* `Jinnah International Airport`, `Port Qasim`, `Gaddafi Stadium`, `Minar-e-Pakistan`, `Tarbela Dam`, `M-2 Motorway`, `Agha Khan University Hospital`, `Badshahi Mosque`.
  - *Negative:* `Aga Khan University` (`EDUCATIONAL_INSTITUTION`), `Lahore` (`CITY`).

### C. Sports & Geopolitical Context: `SPORTS_TEAM` vs `COUNTRY` vs `CITY`
* When a country or city name is used to denote an athletic team competing in a sporting context, tag as `SPORTS_TEAM`.
  - *Sports Team Context:* `"In the final test match, [Pakistan]_SPORTS_TEAM defeated [England]_SPORTS_TEAM by 152 runs."`
  - *Geopolitical Context:* `"[Pakistan]_COUNTRY signed a bilateral trade pact with [England]_COUNTRY."`
* PSL franchises and domestic squads are always `SPORTS_TEAM`.
  - *Positive:* `Karachi Kings`, `Lahore Qalandars`, `Islamabad United`, `Peshawar Zalmi`, `Quetta Gladiators`, `Multan Sultans`, `Shaheens`.

### D. Events: `EVENT` vs `ORGANIZATION`
* **`EVENT`:** Tournaments, recurring sporting competitions, political elections, summits, historical conferences, fiscal budgets, and natural disaster incidents.
  - *Positive:* `Pakistan Super League` (`PSL 10`), `ICC Champions Trophy 2025`, `General Elections 2024`, `Federal Budget 2025-26`, `Independence Day`, `Operation Zarb-e-Azb`.
  - *Negative:* `Pakistan Cricket Board` (`ORGANIZATION`), `Election Commission of Pakistan` (`GOVERNMENT_BODY`).

### E. Media & Politics: `MEDIA_OUTLET`, `POLITICAL_PARTY`, `LAW_ACT`
* **`MEDIA_OUTLET`:** News agencies, newspapers, television broadcast channels, digital media publications, and radio stations.
  - *Positive:* `Dawn`, `The News International`, `Geo News`, `ARY News`, `Daily Jang`, `Express Tribune`, `PTV News`, `BBC Urdu`, `Samaa TV`.
* **`POLITICAL_PARTY`:** Registered political parties, parliamentary alliances, and student political unions.
  - *Positive:* `Pakistan Muslim League-Nawaz` (`PML-N`), `Pakistan Tehreek-e-Insaf` (`PTI`), `Pakistan Peoples Party` (`PPP`), `Muttahida Qaumi Movement-Pakistan` (`MQM-P`), `Jamaat-e-Islami` (`JI`), `JUI-F`.
* **`LAW_ACT`:** Formal statutes, legislative acts, constitutional articles/amendments, legal ordinances, and legal codes.
  - *Positive:* `Constitution of Pakistan`, `Pakistan Penal Code`, `Anti-Terrorism Act 1997`, `Prevention of Electronic Crimes Act` (`PECA`), `26th Constitutional Amendment`, `Article 63-A`.

### F. Structured Values & Expressions
* **`MONEY`:** Currency designator + numerical value + scale denomination.
  - *Include units:* `Rs 500`, `PKR 4.5 billion`, `USD 20 million`, `15 کروڑ روپے`, `12 لاکھ روپے۔`
  - *Rule:* Always include `Rs`, `PKR`, `$`, `crore`, `lakh`, `arab`, `billion`, `million` inside the span.
* **`PERCENT`:** Numerical value + percentage symbol or word.
  - *Include symbols:* `17.5%`, `5.2 percent`, `12 per cent`, `8.4 فیصد`.
* **`DATE`:** Full calendar dates, days of the week, calendar months, and relative dates.
  - *Positive:* `14 August 1947`, `March 23, 1940`, `Monday`, `last Friday`, `yesterday`, `یکم ستمبر`, `۱۰ محرم`.
* **`TIME`:** Specific clock times, hour markers, and time zones.
  - *Positive:* `11:30 AM`, `02:00 PST`, `5 o'clock`, `noon`, `ساڑھے تین بجے`.
* **`PHONE_NUMBER` (100% Synthetic):** Pakistani landlines and mobile numbers.
  - *Positive:* `+92 300 1234567`, `0321-7654321`, `021-34567890`, `00923331234567`.
* **`ID_NUMBER` (100% Synthetic CNIC):** 13-digit Pakistani national identity card format.
  - *Positive:* `42101-1234567-1`, `35201-7654321-9`, `6110198765432`.

---

## 3. Bilingual (Urdu Script) Rules & Transliterations
1. **Eastern Arabic Numerals:** Digits `۰-۹` in dates, currency, percent, phone, and CNIC must be captured with the identical schema.
2. **Urdu Transliterations:** Roman Urdu phrases representing entities must be tagged strictly matching English rules (e.g. `[Wazir-e-Azam]_TITLE` excluded, `[Adalat-e-Uzma]_COURT_LEGAL_BODY`, `[Hukumat-e-Pakistan]_GOVERNMENT_BODY`).
3. **Arabic/Urdu Character Harmonization:** Arabic `ي` (U+064A) and `ك` (U+0643) should be normalized to Urdu `ی` (U+06CC) and `ک` (U+06A9) before matching gazetteers.

---

## 4. Decision Matrix Summary

| Input Text Sample | Contained Candidate | Correct Tag | Rationale |
| :--- | :--- | :--- | :--- |
| "Justice Qazi Faez Isa announced the verdict" | Qazi Faez Isa | `PERSON` | Strip title "Justice" |
| "hearing in Lahore High Court" | Lahore High Court | `COURT_LEGAL_BODY` | Longest span; overrides "Lahore" (CITY) |
| "departs from Jinnah International Airport" | Jinnah International Airport | `LANDMARK_FACILITY` | Longest span; overrides "Jinnah" (PERSON) |
| "enrolled at Punjab University" | Punjab University | `EDUCATIONAL_INSTITUTION` | Longest span; overrides "Punjab" (PROVINCE) |
| "Pakistan beat Australia in Melbourne" | Pakistan | `SPORTS_TEAM` | Cricket competition context |
| "exports from Pakistan to Australia increased" | Pakistan | `COUNTRY` | Geopolitical sovereign entity |
| "dawn of a new era reported by Dawn" | Dawn (2nd occurrence) | `MEDIA_OUTLET` | Common noun vs newspaper brand |
| "passed the Elections Act, 2017" | Elections Act, 2017 | `LAW_ACT` | Formal statute title |
| "allocated Rs 15.5 billion for health" | Rs 15.5 billion | `MONEY` | Currency symbol + numeric + scale in one span |
| "turnout reached 51.7 per cent" | 51.7 per cent | `PERCENT` | Number and unit together |
| "call on 0300-1234567" | 0300-1234567 | `PHONE_NUMBER` | Synthetic format per Rule 3 |
| "CNIC: 42101-1234567-1" | 42101-1234567-1 | `ID_NUMBER` | Synthetic 13-digit identity card format |

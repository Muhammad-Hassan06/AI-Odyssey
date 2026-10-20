# Annotation Guidelines: Pakistani-Context NER System
**TechFest NER Challenge — Dory's Data Dive (Round 2)**
**Document Version:** 1.0.0 | **Last Updated:** 2026-10-19

---

## 1. General Principles & Core Decision Rules

### 1.1 Flat NER & Specificity Precedence (Longest & Most Specific Span)
Our system outputs flat NER spans (standard BIO / token classification). In cases of nested or multi-label candidates:
- **Rule:** Always annotate the **longest span** representing the **most specific applicable category**.
- *Example:* In `"Karachi University Cricket Team"`, do **not** annotate `"Karachi"` as `CITY` or `"Karachi University"` as `EDUCATIONAL_INSTITUTION`; annotate the complete span as `SPORTS_TEAM`.
- *Example:* In `"Supreme Court Bar Association"`, annotate the entire entity as `ORGANIZATION` rather than `"Supreme Court"` as `COURT_LEGAL_BODY`.

### 1.2 Boundary & Punctuation Rules
- **No leading or trailing punctuation:** Spans must never start or end with commas, periods, quotes, brackets, or semicolons unless intrinsic to the formal name.
  - *Correct:* `[Dawn]` reported...
  - *Incorrect:* `[Dawn,]` reported...
- **Possessive Markers:** Strip apostrophes and possessive `'s` or `s'` from the entity span.
  - *Correct:* `[Bilawal Bhutto Zardari]'s statement...
  - *Incorrect:* `[Bilawal Bhutto Zardari's] statement...`
- **Honorifics, Professional & Political Titles:** Honorifics (e.g., *Mr.*, *Ms.*, *Dr.*, *Justice*, *Justice (retd)*, *Prime Minister*, *Senator*, *Field Marshal*, *Maulana*, *Syed*, *Barrister*) are **excluded** from `PERSON` spans unless historically inseparable from a recognized mononym.
  - *Correct:* Prime Minister `[Shehbaz Sharif]`, Justice `[Qazi Faez Isa]`, Dr `[Abdul Qadeer Khan]`
  - *Incorrect:* `[Prime Minister Shehbaz Sharif]`, `[Justice Qazi Faez Isa]`
  - *Urdu Honorifics:* جناب (Janab), صاحب (Sahab), محترم (Mohtaram) are excluded: `[عمران خان]` صاحب.

### 1.3 Multilingual & Transliteration Consistency
- The guidelines apply identically across **English**, **Urdu script**, and **Roman Urdu**.
- Common Pakistani English abbreviations (e.g., *PTI*, *SBP*, *LUMS*, *SC*, *IHC*) receive their respective specific category.
- Urdu diacritics / variants (e.g., *Karachi*, *Karāchi*, *کراچی*) share the identical label (`CITY`).

---

## 2. Resolving Confusable Category Pairs (Decision Matrix)

| Entity Pair | Decision Rule & Examples |
| :--- | :--- |
| **GOVERNMENT_BODY vs. ORGANIZATION** | State ministries, executive departments, municipal authorities, law enforcement agencies, and regulatory commissions (e.g., *Ministry of Finance*, *FBR*, *SECP*, *Sindh Police*, *NADRA*) are `GOVERNMENT_BODY`. Commercial enterprises (even state-owned like *PIA*, *OGDCL*), political parties, international NGOs, charities (e.g., *Edhi Foundation*), and private companies are `ORGANIZATION`. |
| **COURT_LEGAL_BODY vs. GOVERNMENT_BODY / ORG** | Courts of law, tribunals, judicial commissions, and legal registries (e.g., *Supreme Court of Pakistan*, *Lahore High Court*, *Judicial Commission of Pakistan*, *Banking Court*) are strictly `COURT_LEGAL_BODY`. Bar associations and law firms are `ORGANIZATION`. Administrative bodies (e.g., *Ministry of Law*) are `GOVERNMENT_BODY`. |
| **POLITICAL_PARTY vs. ORGANIZATION** | Registered political parties, parliamentary electoral alliances, and student political wings (e.g., *PTI*, *PML-N*, *PPP*, *MQM-P*, *JI*, *JUI-F*, *ANP*, *PDM*) are strictly `POLITICAL_PARTY`. Non-partisan unions, chambers of commerce, and advocacy NGOs are `ORGANIZATION`. |
| **CITY vs. PROVINCE_REGION vs. COUNTRY** | Specific municipalities, towns, cantonments, and tehsils (e.g., *Karachi*, *Lahore*, *Rawalpindi*, *Gwadar*) are `CITY`. Sub-national federating units, autonomous territories, administrative divisions, and geographic regions (e.g., *Punjab*, *Sindh*, *Khyber Pakhtunkhwa*, *Balochistan*, *Gilgit-Baltistan*, *Azad Jammu and Kashmir*, *Potohar*, *Thar Desert*) are `PROVINCE_REGION`. Sovereign nations are `COUNTRY`. |
| **LANDMARK_FACILITY vs. EDUCATIONAL_INSTITUTION / ORG** | Public infrastructure, monuments, stadiums, airports, ports, historic mosques, hospitals, and dams (e.g., *Minar-e-Pakistan*, *Jinnah International Airport*, *Badshahi Mosque*, *National Stadium Karachi*, *Shaukat Khanum Hospital*, *M-2 Motorway*, *Tarbela Dam*) are `LANDMARK_FACILITY`. However, autonomous degree-awarding universities, colleges, and schools are specifically `EDUCATIONAL_INSTITUTION`. |
| **SPORTS_TEAM vs. ORGANIZATION** | Franchise teams, national sports squads, and departmental sports teams (e.g., *Karachi Kings*, *Lahore Qalandars*, *Pakistan National Cricket Team*, *WAPDA Football Club*) are `SPORTS_TEAM`. Sports governing boards (e.g., *Pakistan Cricket Board (PCB)*, *Pakistan Olympic Association*) are `ORGANIZATION`. |
| **LAW_ACT vs. GOVERNMENT_BODY / EVENT** | Enacted legislation, ordinances, constitutional amendments, legal codes, and formal bills (e.g., *Pakistan Penal Code*, *PECA 2016*, *26th Constitutional Amendment*, *Article 63-A*) are `LAW_ACT`. The legislative bodies enacting them (e.g., *National Assembly*) are `GOVERNMENT_BODY`. |
| **MONEY vs. PERCENT vs. ID_NUMBER** | Currencies and amounts (including symbols/prefixes like *Rs*, *PKR*, *USD*, *crore*, *billion*) belong strictly to `MONEY` (e.g., `[Rs 500 million]`, `[PKR 12.5 billion]`). Ratios and percentage expressions (including *%* and *per cent*) belong to `PERCENT` (e.g., `[5.2 per cent]`, `[14%]`). Numeric national identity identifiers (13 digits or `xxxxx-xxxxxxx-x`) are `ID_NUMBER`. |
| **DATE vs. TIME vs. EVENT** | Calendar dates, days, months, and relative dates are `DATE`. Clock times, durations, and specific timestamps are `TIME`. Recurring named celebrations, festivals, tournaments, summits, or wars (e.g., *PSL 10*, *Independence Day*, *Eid-ul-Fitr*, *COP29*, *Budget 2025-26*) are `EVENT`. |

---

## 3. Comprehensive Entity Catalog (Definitions & Examples)

### 1. `PERSON`
- **Definition:** Real or fictional human beings, referenced by proper given names, surnames, or widely recognized single names.
- **Positive Examples:**
  1. `[Muhammad Ali Jinnah]` addressed the gathering.
  2. The speech delivered by `[Maryam Nawaz]` drew applause.
  3. شاعرِ مشرق `[علامہ اقبال]` نے خواب دیکھا۔
- **Negative Examples:**
  1. `[Prime Minister]` Shehbaz Sharif (*Prime Minister* is a title, not part of `PERSON`).
  2. `[Jinnah International Airport]` (*Airport is a `LANDMARK_FACILITY`, not a person*).

### 2. `CITY`
- **Definition:** Specific named human settlements: cities, towns, villages, tehsils, and union councils.
- **Positive Examples:**
  1. Heavy rainfall flooded low-lying areas of `[Karachi]`.
  2. The trade convoy departed from `[Faisalabad]` early morning.
  3. تجارتی قافلہ `[پشاور]` پہنچ گیا۔
- **Negative Examples:**
  1. The provincial government of `[Sindh]` (*Sindh is `PROVINCE_REGION`*).
  2. `[Karachi Port Trust]` (*Autonomous entity is `ORGANIZATION` / `GOVERNMENT_BODY`*).

### 3. `PROVINCE_REGION`
- **Definition:** Sub-national administrative units, provinces, divisions, territories, and well-defined geographic/cultural regions.
- **Positive Examples:**
  1. The assembly of `[Punjab]` passed the resolution unanimously.
  2. Tourism witnessed a surge in `[Gilgit-Baltistan]` and `[Azad Kashmir]`.
  3. شدید سیلاب نے `[بلوچستان]` کے کئی اضلاع کو متاثر کیا۔
- **Negative Examples:**
  1. Bilateral talks with `[Pakistan]` (*Pakistan is `COUNTRY`*).
  2. The city of `[Quetta]` (*Quetta is `CITY`*).

### 4. `COUNTRY`
- **Definition:** Sovereign nations, nation-states, and independent geopolitical territories.
- **Positive Examples:**
  1. Foreign delegates arrived in `[Pakistan]` for the regional summit.
  2. Commercial agreements were executed between `[China]` and `[Saudi Arabia]`.
  3. `[پاکستان]` اور برادر اسلامی ملک کے درمیان معاہدہ ہوا۔
- **Negative Examples:**
  1. The ambassador met leaders in `[Islamabad]` (*Islamabad is `CITY`*).
  2. Exporting to `[Khyber Pakhtunkhwa]` (*KP is `PROVINCE_REGION`*).

### 5. `LANDMARK_FACILITY`
- **Definition:** Man-made infrastructure, architectural monuments, transportation hubs (airports, ports, railway stations, dry ports), dams, public parks, highways, motorways, hospitals, and stadiums.
- **Positive Examples:**
  1. The rally congregated around `[Minar-e-Pakistan]` before evening.
  2. International flights landed safely at `[Allama Iqbal International Airport]`.
  3. مریضوں کو فوری طور پر `[نشتر ہسپتال]` منتقل کیا گیا۔
- **Negative Examples:**
  1. He enrolled at `[Quaid-e-Azam University]` (*University is `EDUCATIONAL_INSTITUTION`*).
  2. The headquarters of `[National Bank of Pakistan]` (*Bank is `ORGANIZATION`*).

### 6. `GOVERNMENT_BODY`
- **Definition:** State executive organs, ministries, secretariats, civil service bodies, regulatory commissions, municipal corporations, law enforcement, and military commands.
- **Positive Examples:**
  1. The `[Federal Board of Revenue]` surpassed the quarterly tax collection target.
  2. Directives were issued by the `[Ministry of Foreign Affairs]`.
  3. `[الیکشن کمیشن آف پاکستان]` نے شیڈول جاری کیا۔
- **Negative Examples:**
  1. A hearing in the `[Islamabad High Court]` (*Courts are strictly `COURT_LEGAL_BODY`*).
  2. Spokesman for `[Pakistan Peoples Party]` (*Party is `POLITICAL_PARTY`*).

### 7. `POLITICAL_PARTY`
- **Definition:** Legally registered political parties, parliamentary alliances, political coalitions, and formal political student federations.
- **Positive Examples:**
  1. The core committee of `[Pakistan Tehreek-e-Insaf]` met in Islamabad.
  2. Leaders of `[PML-N]` and `[PPP]` agreed on the coalition formula.
  3. جلسے میں `[جماعت اسلامی]` کے کارکنان کثیر تعداد میں شریک ہوئے۔
- **Negative Examples:**
  1. Delegations from the `[Karachi Chamber of Commerce]` (*Chamber is `ORGANIZATION`*).
  2. Resolution presented in the `[Senate of Pakistan]` (*Senate is `GOVERNMENT_BODY`*).

### 8. `ORGANIZATION`
- **Definition:** Commercial companies, state-owned corporations, NGOs, charities, industrial groups, trade unions, bar associations, and international alliances.
- **Positive Examples:**
  1. Shares of `[Oil and Gas Development Company Limited]` rose by 3 points.
  2. Emergency relief was mobilized by the `[Edhi Foundation]`.
  3. `[پاکستان ریلوے]` نے کرایوں میں کمی کا اعلان کیا۔
- **Negative Examples:**
  1. Tax audits managed by `[FBR]` (*FBR is `GOVERNMENT_BODY`*).
  2. Courses registered at `[IBA Karachi]` (*IBA is `EDUCATIONAL_INSTITUTION`*).

### 9. `EDUCATIONAL_INSTITUTION`
- **Definition:** Degree-granting universities, educational boards (BISE), degree colleges, academies, polytechnics, and schools.
- **Positive Examples:**
  1. Computer Science students at `[LUMS]` presented their final projects.
  2. The syndicate meeting was convened at `[University of the Punjab]`.
  3. داخلوں کا آغاز `[جامعہ کراچی]` میں کر دیا گیا۔
- **Negative Examples:**
  1. Financial grants allocated by `[Higher Education Commission]` (*HEC is a regulatory `GOVERNMENT_BODY`*).
  2. Match held at `[Gaddafi Stadium]` (*Stadium is `LANDMARK_FACILITY`*).

### 10. `COURT_LEGAL_BODY`
- **Definition:** Judicial courts, benches, judicial commissions, appellate tribunals, and judicial arbitration councils.
- **Positive Examples:**
  1. A larger bench of the `[Supreme Court of Pakistan]` reserved its verdict.
  2. The petition was filed before the `[Peshawar High Court]`.
  3. `[سندھ ہائیکورٹ]` نے تحریری حکم نامہ جاری کر دیا۔
- **Negative Examples:**
  1. Statement made by the `[Ministry of Law and Justice]` (*Ministry is `GOVERNMENT_BODY`*).
  2. Members of the `[Karachi Bar Association]` (*Bar Association is `ORGANIZATION`*).

### 11. `LAW_ACT`
- **Definition:** Formal legislative acts, legal statutes, constitutional provisions, presidential ordinances, and formal penal/civil codes.
- **Positive Examples:**
  1. The accused was booked under Section 302 of the `[Pakistan Penal Code]`.
  2. Regulatory compliance under `[PECA 2016]` was reviewed by the committee.
  3. پارلیمنٹ نے `[26 ویں آئینی ترمیم]` کی منظوری دی۔
- **Negative Examples:**
  1. Session called in the `[National Assembly]` (*Parliamentary body is `GOVERNMENT_BODY`*).
  2. Celebration of `[Constitution Day]` (*Holiday/observance is `EVENT`*).

### 12. `EVENT`
- **Definition:** Named historical incidents, natural disasters, sports tournaments, budget presentations, conferences, military conflicts, and national commemorations.
- **Positive Examples:**
  1. The opening ceremony of `[PSL 2025]` took place in Lahore.
  2. Nationwide activities marked the celebration of `[Pakistan Day]`.
  3. حکومتی ترجمان نے `[بجٹ 2025-26]` کے اہم خدوخال پیش کیے۔
- **Negative Examples:**
  1. The event starts on `[Monday]` (*Calendar day is `DATE`*).
  2. The champion team was `[Lahore Qalandars]` (*Franchise is `SPORTS_TEAM`*).

### 13. `MEDIA_OUTLET`
- **Definition:** News broadcast channels, daily newspapers, digital journalism portals, radio services, and news press agencies.
- **Positive Examples:**
  1. An investigation published in `[Dawn]` revealed budgetary discrepancies.
  2. The breaking bulletin was telecast across `[Geo News]`.
  3. تفصیلات `[روزنامہ جنگ]` میں شائع کی گئیں۔
- **Negative Examples:**
  1. Press release issued by the `[Press Information Department]` (*PID is `GOVERNMENT_BODY`*).
  2. Advertisement posted by `[Daraz.pk]` (*E-commerce platform is `ORGANIZATION`*).

### 14. `SPORTS_TEAM`
- **Definition:** National sports squads, franchise teams, and competitive sports clubs.
- **Positive Examples:**
  1. A commanding victory was registered by `[Karachi Kings]` in the final.
  2. The selection squad for the `[Pakistan National Cricket Team]` was finalized.
  3. شائقین نے `[اسلام آباد یونائیٹڈ]` کی جیت کا جشن منایا۔
- **Negative Examples:**
  1. Management regulations updated by the `[Pakistan Cricket Board]` (*PCB is `ORGANIZATION`*).
  2. Match hosted at `[Rawalpindi Cricket Stadium]` (*Stadium is `LANDMARK_FACILITY`*).

### 15. `DATE`
- **Definition:** Specific calendar days, dates of the month, named months, years, and relative calendar references.
- **Positive Examples:**
  1. The notification will take effect from `[14 August 2025]`.
  2. Heavy trading was observed on `[Monday]`.
  3. نیا تعلیمی سال `[یکم ستمبر]` سے شروع ہوگا۔
- **Negative Examples:**
  1. The conference adjourned at `[3:30 PM]` (*Clock timestamp is `TIME`*).
  2. Festive gatherings for `[Eid-ul-Adha]` (*Religious festival is `EVENT`*).

### 16. `TIME`
- **Definition:** Specific clock times, hours, timestamps, and stated duration intervals.
- **Positive Examples:**
  1. The emergency siren sounded at `[11:45 PM]` sharp.
  2. Power outages were scheduled between `[02:00 PST]` and `[06:00 PST]`.
  3. اجلاس ٹھیک `[ساڑھے تین بجے]` منعقد ہوگا۔
- **Negative Examples:**
  1. Submission deadline is `[next Tuesday]` (*Day of week is `DATE`*).
  2. Historic events of `[May 9]` (*Date is `DATE`*).

### 17. `MONEY`
- **Definition:** Monetary sums, amounts, financial denominations including symbols and scale suffixes (*Rs*, *PKR*, *USD*, *crore*, *lakh*, *billion*). The symbol/unit **must be included inside the span**.
- **Positive Examples:**
  1. The project allocation was raised to `[Rs 45.8 billion]`.
  2. Remittances exceeded `[PKR 300,000]` per household.
  3. کل تخمینہ `[15 کروڑ روپے]` لگایا گیا ہے۔
- **Negative Examples:**
  1. An inflation increase of `[8.5%]` (*Rate of change is `PERCENT`*).
  2. The registered vehicle serial was `[125000]` (*Generic number without currency is `O`*).

### 18. `PERCENT`
- **Definition:** Percentages, fractional percentage points, and ratio metrics including *%*, *per cent*, or *فیصد*. The indicator symbol/word **must be included inside the span**.
- **Positive Examples:**
  1. The central bank hiked the policy rate to `[17.5 per cent]`.
  2. The export quota expanded by `[12.4%]`.
  3. زرعی پیداوار میں `[4.8 فیصد]` اضافہ دیکھا گیا۔
- **Negative Examples:**
  1. Net profits totaled `[Rs 500 million]` (*Currency is `MONEY`*).
  2. A ratio of `[3 out of 10]` (*Non-percentage proportion is `O`*).

### 19. `PHONE_NUMBER`
- **Definition:** Pakistani phone numbers across landline, mobile, toll-free, and emergency contact formats. **Must be 100% synthetic/generated numbers.**
- **Positive Examples:**
  1. For complaints, dial our helpline at `[+92 300 1234567]`.
  2. Verification calls will originate from `[021-34567890]`.
  3. شکایات کے اندراج کے لیے `[0321-9876543]` پر رابطہ کریں۔
- **Negative Examples:**
  1. Verification verified through CNIC `[42101-1234567-1]` (*CNIC is `ID_NUMBER`*).
  2. The zip code of the district is `[44000]` (*Postal code is `O`*).

### 20. `ID_NUMBER`
- **Definition:** Pakistani Computerized National Identity Card (CNIC) numbers, National Identity Cards for Overseas Pakistanis (NICOP), and 13-digit identity numbers. **Must be 100% synthetic/generated numbers.**
- **Positive Examples:**
  1. Candidate with CNIC `[42201-1234567-3]` was selected.
  2. Unhyphenated card records showed `[6110198765432]`.
  3. امیدوار کا شناختی کارڈ نمبر `[35201-7654321-9]` تصدیق کے لیے پیش کیا گیا۔
- **Negative Examples:**
  1. Registered helpline contact `[0300-1234567]` (*Mobile number is `PHONE_NUMBER`*).
  2. Case file registration `[CR-2024-998]` (*Judicial case code is `O`*).

---

## 4. Annotation Boundary Checklist for Annotators

1. **Exact 20 Tags:** Never assign or create tags outside the 20 listed categories.
2. **Include Currency & Percent Signs:** Always include `Rs`, `PKR`, `$`, `crore`, `%`, `per cent`, `فیصد` inside `MONEY` or `PERCENT`.
3. **Exclude Titles:** Exclude `Dr.`, `Mr.`, `Justice`, `Prime Minister`, `صاحب` from `PERSON`.
4. **No Punctuation Spillovers:** Check that closing commas, quotation marks, or brackets do not leak into the tagged span.
5. **No Real PII:** In the event any real phone number or real CNIC is observed in source text, replace it immediately with a synthetic pattern prior to annotation.

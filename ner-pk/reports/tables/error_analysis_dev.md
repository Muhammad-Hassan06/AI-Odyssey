# Error Analysis & Diagnostic Log (DEV Split)

## Boundary Mismatches (13 occurrences)

- **Issue:** Boundary offset mismatch: gold (12:19) vs pred (12:24)
  - *Sentence:* "انگریزوں نے 3 فروری 1839ء کو کراچی شہر پر حملہ کیا اور اس پر قبضہ کر لیا۔"

- **Issue:** Boundary offset mismatch: gold (155:160) vs pred (148:160)
  - *Sentence:* "This renaming by the Pakistan Cricket Board (PCB) is part of an effort to modernise the stadium and honour national leaders Muhammad Ali Jinnah and Allama Iqbal."

- **Issue:** Boundary offset mismatch: gold (9:14) vs pred (9:23)
  - *Sentence:* "The 2004 India-Pakistan series was a historic bilateral cricket series as it marked return of first full India-Pakistan series since 1989 known "Friendship Series", marking the resumption of cricketing ties between the two arch-rivals after nearly 15 years of limited interactions due to political tensions."

- **Issue:** Boundary offset mismatch: gold (15:23) vs pred (9:23)
  - *Sentence:* "The 2004 India-Pakistan series was a historic bilateral cricket series as it marked return of first full India-Pakistan series since 1989 known "Friendship Series", marking the resumption of cricketing ties between the two arch-rivals after nearly 15 years of limited interactions due to political tensions."

- **Issue:** Boundary offset mismatch: gold (105:110) vs pred (105:119)
  - *Sentence:* "The 2004 India-Pakistan series was a historic bilateral cricket series as it marked return of first full India-Pakistan series since 1989 known "Friendship Series", marking the resumption of cricketing ties between the two arch-rivals after nearly 15 years of limited interactions due to political tensions."

- **Issue:** Boundary offset mismatch: gold (111:119) vs pred (105:119)
  - *Sentence:* "The 2004 India-Pakistan series was a historic bilateral cricket series as it marked return of first full India-Pakistan series since 1989 known "Friendship Series", marking the resumption of cricketing ties between the two arch-rivals after nearly 15 years of limited interactions due to political tensions."

- **Issue:** Boundary offset mismatch: gold (4:12) vs pred (4:18)
  - *Sentence:* "The Pakistan-India War of 1965 led to reduced foreign economic assistance, impacting the growth rate of large-scale manufacturing."

- **Issue:** Boundary offset mismatch: gold (13:18) vs pred (4:18)
  - *Sentence:* "The Pakistan-India War of 1965 led to reduced foreign economic assistance, impacting the growth rate of large-scale manufacturing."

## Type Confusions (6 occurrences)

- **Issue:** Type confusion: gold 'COUNTRY' predicted as 'GOVERNMENT_BODY'
  - *Sentence:* "سن 2000ء میں حکومت پاکستان نے سیاسی، انتظامی اور مالی وسائل اور ذمہ داریوں کو نچلی سطح تک منتقل کرنے کا منصوبہ بنایا۔"

- **Issue:** Type confusion: gold 'CITY' predicted as 'LANDMARK_FACILITY'
  - *Sentence:* "کراچی پورٹ ٹرسٹ 20 ارب روپے کے ایک منصوبے پورٹ ٹاور کمپلیکس کا آغاز کر رہی ہے جو ایک ہزار 947 فٹ بلندی کے ساتھ پاکستان کی سب سے بلند عمارت ہوگی۔"

- **Issue:** Type confusion: gold 'CITY' predicted as 'LANDMARK_FACILITY'
  - *Sentence:* "ملک کی سب سے بڑی بندرگاہیں بھی کراچی میں قائم ہیں جو کراچی پورٹ اور پورٹ قاسم کہلاتی ہیں۔"

- **Issue:** Type confusion: gold 'EVENT' predicted as 'COUNTRY'
  - *Sentence:* "پاکستان سپر لیگ کے پرامن انعقاد کے لیے فیصل آباد میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

- **Issue:** Type confusion: gold 'EVENT' predicted as 'COUNTRY'
  - *Sentence:* "پاکستان سپر لیگ کے پرامن انعقاد کے لیے سیالکوٹ میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

- **Issue:** Type confusion: gold 'POLITICAL_PARTY' predicted as 'COUNTRY'
  - *Sentence:* "پاکستان مسلم لیگ (ن) کے مرکزی وفد نے راولپنڈی میں پریس کانفرنس سے خطاب کیا۔"

## False Negatives (23 occurrences)

- **Issue:** Missed entity: '26ویں آئینی ترمیم' [LAW_ACT]
  - *Sentence:* "انسداد دہشت گردی عدالت نے 26ویں آئینی ترمیم کے تحت دائر آئینی درخواست کی سماعت اتوار تک ملتوی کر دی۔"

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The tender quotation reference was TND/939/2021 issued in 2021."

- **Issue:** Missed entity: '۶۸۱۶۲۶۱۹۲۱۰۰۱' [ID_NUMBER]
  - *Sentence:* "امیدوار کا قومی شناختی کارڈ نمبر ۶۸۱۶۲۶۱۹۲۱۰۰۱ برائے تصدیق جمع کرایا گیا۔"

- **Issue:** Missed entity: 'یوم آزادی' [EVENT]
  - *Sentence:* "یوم آزادی کے پرامن انعقاد کے لیے کوئٹہ میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

- **Issue:** Missed entity: 'عام انتخابات 2024' [EVENT]
  - *Sentence:* "عام انتخابات 2024 کے پرامن انعقاد کے لیے کوئٹہ میں سیکیورٹی کے فول پروف انتظامات کیے گئے۔"

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The case reference was registered under file number WP-6309/2023 in 2023."

- **Issue:** Missed entity: '26ویں آئینی ترمیم' [LAW_ACT]
  - *Sentence:* "سپریم کورٹ آف پاکستان کے دو رکنی بینچ نے فیصل آباد میں 26ویں آئینی ترمیم کے نفاذ کا اہم حکم جاری کیا۔"

- **Issue:** Missed entity: '' [CITY]
  - *Sentence:* "The tender quotation reference was TND/326/2026 issued in 2026."

## False Positives (145 occurrences)

- **Issue:** Spurious entity: 'Hazara' [PROVINCE_REGION]
  - *Sentence:* "The city has a number of government and private colleges, including the following:

Football is the most popular sport among the people of Quetta.[51][52] The city has produced notable footballers for the Pakistan national football team including Abdul Wahid Durrani, Qayyum Changezi, Ayub Dar, Mohammad Ali, and Rajab Ali Hazara.[53] Main football clubs from Quetta include Baloch Quetta, Hazara Club Quetta."

- **Issue:** Spurious entity: 'Hazara' [PROVINCE_REGION]
  - *Sentence:* "The city has a number of government and private colleges, including the following:

Football is the most popular sport among the people of Quetta.[51][52] The city has produced notable footballers for the Pakistan national football team including Abdul Wahid Durrani, Qayyum Changezi, Ayub Dar, Mohammad Ali, and Rajab Ali Hazara.[53] Main football clubs from Quetta include Baloch Quetta, Hazara Club Quetta."

- **Issue:** Spurious entity: 'جنگ' [MEDIA_OUTLET]
  - *Sentence:* "اس سال سندھ کے حکمرانوں اور خان قلات کے درمیان میں جنگ چھڑ گئی اور کراچی پر سندھ کی حکومت کا قبضہ ہو گیا۔"

- **Issue:** Spurious entity: 'جنگ' [MEDIA_OUTLET]
  - *Sentence:* "1857ء کی جنگ آزادی کے دوران میں کراچی میں 21 ویں نیٹِو انفنٹری نے 10 ستمبر کو مغل فرمانروا بہادر شاہ ظفر سے بیعت کر لی۔"

- **Issue:** Spurious entity: 'پورٹ قاسم' [LANDMARK_FACILITY]
  - *Sentence:* "ملک کی سب سے بڑی بندرگاہیں بھی کراچی میں قائم ہیں جو کراچی پورٹ اور پورٹ قاسم کہلاتی ہیں۔"

- **Issue:** Spurious entity: 'سمندری' [CITY]
  - *Sentence:* "یہ بندرگاہیں جدید سہولیات سے مزین ہیں اور نہ صرف پاکستان کی تمام تجارتی ضروریات کے مطابق کام کرتی ہیں بلکہ افغانستان اور وسط ایشیاء کے ممالک کی سمندری تجارت بھی انہی بندرگاہوں سے ہوتی ہے۔"

- **Issue:** Spurious entity: 'اتوار' [DATE]
  - *Sentence:* "پشاور ہائی کورٹ نے مجموعہ تعزیرات پاکستان کے تحت دائر آئینی درخواست کی سماعت اتوار تک ملتوی کر دی۔"

- **Issue:** Spurious entity: 'Saturday' [DATE]
  - *Sentence:* "A symposium on modern computing was organized jointly at Aga Khan University in Multan on Saturday."


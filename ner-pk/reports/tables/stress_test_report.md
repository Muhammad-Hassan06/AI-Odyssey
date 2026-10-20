# Out-of-Domain Robustness Stress Test

### Urdu Script: Entity Recall = 100.0%
- **Input:** "سندھ ہائیکورٹ نے وفاقی وزیر کی ضمانت منظور کر لی۔"
  - Targets: ['سندھ ہائیکورٹ']
  - Extracted: ['سندھ ہائیکورٹ [COURT_LEGAL_BODY]']

- **Input:** "عمران خان نے اسلام آباد میں بڑے جلسے سے خطاب کیا۔"
  - Targets: ['عمران خان', 'اسلام آباد']
  - Extracted: ['عمران خان [PERSON]', 'اسلام آباد [CITY]']

- **Input:** "حکومت نے بجٹ میں 15 کروڑ روپے کی گرانٹ جاری کی۔"
  - Targets: ['15 کروڑ روپے']
  - Extracted: ['15 کروڑ روپے [MONEY]']

### Roman Urdu Transliterations: Entity Recall = 100.0%
- **Input:** "Supreme Court ne wazir-e-azam ki appeal reject kardi in Islamabad."
  - Targets: ['Supreme Court', 'Islamabad']
  - Extracted: ['Supreme Court [COURT_LEGAL_BODY]', 'Islamabad [CITY]']

- **Input:** "Karachi Kings ne match Jeet liya Lahore Qalandars ke khilaf."
  - Targets: ['Karachi Kings', 'Lahore Qalandars']
  - Extracted: ['Karachi Kings [SPORTS_TEAM]', 'Lahore Qalandars [SPORTS_TEAM]']

- **Input:** "NAB ne 500 million rupees recover kar liye."
  - Targets: ['NAB', '500 million rupees']
  - Extracted: ['NAB [GOVERNMENT_BODY]', '500 million rupees [MONEY]']

### ALL-CAPS Headlines: Entity Recall = 100.0%
- **Input:** "PRIME MINISTER VISITS LAHORE FOR EMERGENCY FLOOD RELIEF MEETING"
  - Targets: ['LAHORE']
  - Extracted: ['LAHORE [CITY]']

- **Input:** "STATE BANK OF PAKISTAN HIKES POLICY RATE TO 17.5 PERCENT"
  - Targets: ['STATE BANK OF PAKISTAN', '17.5 PERCENT']
  - Extracted: ['STATE BANK OF PAKISTAN [GOVERNMENT_BODY]', '17.5 PERCENT [PERCENT]']

- **Input:** "ISLAMABAD UNITED LIFTS PSL TROPHY IN FRONT OF THOUSANDS"
  - Targets: ['ISLAMABAD UNITED', 'PSL']
  - Extracted: ['ISLAMABAD UNITED [SPORTS_TEAM]', 'PSL [EVENT]']

### All-Lowercase Text: Entity Recall = 100.0%
- **Input:** "petitioner approached peshawar high court under peca 2016."
  - Targets: ['peshawar high court', 'peca 2016']
  - Extracted: ['peshawar high court [COURT_LEGAL_BODY]', 'peca 2016 [LAW_ACT]']

- **Input:** "national database and registration authority issued cnic 35201-7654321-9."
  - Targets: ['national database and registration authority', '35201-7654321-9']
  - Extracted: ['national database and registration authority [GOVERNMENT_BODY]', '35201-7654321-9 [ID_NUMBER]']

- **Input:** "dawn newspaper reported high inflation in karachi on monday."
  - Targets: ['dawn', 'karachi', 'monday']
  - Extracted: ['dawn [MEDIA_OUTLET]', 'karachi [CITY]', 'monday [DATE]']

### Typo & OCR Noise: Entity Recall = 100.0%
- **Input:** "Emergency helpline dial +92-300-l234567 or 021-3456789O."
  - Targets: ['+92-300-l234567']
  - Extracted: ['+92-300-l234567 [PHONE_NUMBER]', '021-3456789O [PHONE_NUMBER]']

- **Input:** "Project expenditure estimated at Rs. l.5 billion in Karach1."
  - Targets: ['Rs. l.5 billion', 'Karach1']
  - Extracted: ['Rs. l.5 billion [MONEY]', 'Karach1 [CITY]']

- **Input:** "The match at Gaddafi Stadium started at ll:45 PM sharp."
  - Targets: ['Gaddafi Stadium']
  - Extracted: ['Gaddafi Stadium [LANDMARK_FACILITY]', 'll:45 PM [TIME]']


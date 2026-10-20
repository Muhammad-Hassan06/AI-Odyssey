# Consistency Pass Changelog: Pakistani-Context NER (Phase 1)
**Standard Enforced:** `docs/annotation_guideline.md` | **Destination:** `ner-pk/v2/`
**Total Corrections Applied:** 120

## Summary of Changes:
1. **Nested & Overlapping Span Resolutions:** Resolved all nested city/team, city/court, and region/facility overlaps using the *Longest Meaningful Span* principle.
2. **Honorific & Title Strippings:** Systematically detached titles (*Mr.*, *Dr.*, *Justice*, *Prime Minister*, etc.) from `PERSON` spans.
3. **Boundary Hygiene:** Stripped trailing punctuation and possessive clitics (`'s`, `’s`).
4. **Article Normalization:** Stripped leading non-brand articles (`the ` / `The `) from organizational and court names.

## Detailed Modification Log (Sample 50 entries):

- [TRAIN #1] Stripped title 'علامہ': 'علامہ اقبال' -> 'اقبال' [PERSON]
- [TRAIN #2] Stripped title 'Allama': 'Allama Iqbal' -> 'Iqbal' [PERSON]
- [TRAIN #3] Stripped title 'Allama': 'Allama Iqbal' -> 'Iqbal' [PERSON]
- [TRAIN #4] Stripped title 'Allama': 'Allama Iqbal' -> 'Iqbal' [PERSON]
- [TRAIN #5] Stripped title 'علامہ': 'علامہ اقبال' -> 'اقبال' [PERSON]
- [TRAIN #6] Stripped leading punct: '(081) 2407191' -> '081) 2407191' [PHONE_NUMBER]
- [TRAIN #7] Stripped leading punct: '(0315) 5545668' -> '0315) 5545668' [PHONE_NUMBER]
- [TRAIN #8] Stripped leading punct: '(0317) 8939898' -> '0317) 8939898' [PHONE_NUMBER]
- [TRAIN #9] Resolved overlap: Kept longer 'کوئٹہ گلیڈی ایٹرز' [SPORTS_TEAM], dropped nested 'کوئٹہ' [CITY] in sentence: "کوئٹہ گلیڈی ایٹرز نے شاندار کھیل کا مظاہرہ کرتے ہوئے کوئٹہ م..."
- [TRAIN #10] Stripped leading punct: '(0345) 7126315' -> '0345) 7126315' [PHONE_NUMBER]
- [TRAIN #11] Resolved overlap: Kept longer 'لاہور ہائی کورٹ' [COURT_LEGAL_BODY], dropped nested 'لاہور' [CITY] in sentence: "لاہور ہائی کورٹ نے مجموعہ تعزیرات پاکستان کے تحت دائر آئینی ..."
- [TRAIN #12] Stripped leading punct: '(0343) 9431498' -> '0343) 9431498' [PHONE_NUMBER]
- [TRAIN #13] Stripped leading punct: '(0302) 2797846' -> '0302) 2797846' [PHONE_NUMBER]
- [TRAIN #14] Stripped leading punct: '(0304) 8991659' -> '0304) 8991659' [PHONE_NUMBER]
- [TRAIN #15] Stripped leading punct: '(091) 8663605' -> '091) 8663605' [PHONE_NUMBER]
- [TRAIN #16] Stripped leading punct: '(091) 7425184' -> '091) 7425184' [PHONE_NUMBER]
- [TRAIN #17] Resolved overlap: Kept longer 'Multan Sultans' [SPORTS_TEAM], dropped nested 'Multan' [CITY] in sentence: "In an exciting match on Friday, Multan Sultans secured victo..."
- [TRAIN #18] Stripped trailing punct: 'پاکستان مسلم لیگ (ن)' -> 'پاکستان مسلم لیگ (ن' [POLITICAL_PARTY]
- [TRAIN #19] Stripped leading punct: '(0305) 6781505' -> '0305) 6781505' [PHONE_NUMBER]
- [TRAIN #20] Stripped leading punct: '(0330) 9859431' -> '0330) 9859431' [PHONE_NUMBER]
- [TRAIN #21] Stripped leading punct: '(022) 8731427' -> '022) 8731427' [PHONE_NUMBER]
- [TRAIN #22] Stripped leading punct: '(022) 9028420' -> '022) 9028420' [PHONE_NUMBER]
- [TRAIN #23] Stripped leading punct: '(0334) 7323826' -> '0334) 7323826' [PHONE_NUMBER]
- [TRAIN #24] Stripped trailing punct: 'پاکستان مسلم لیگ (ن)' -> 'پاکستان مسلم لیگ (ن' [POLITICAL_PARTY]
- [TRAIN #25] Stripped leading punct: '(0336) 9352133' -> '0336) 9352133' [PHONE_NUMBER]
- [TRAIN #26] Stripped leading punct: '(0302) 4156974' -> '0302) 4156974' [PHONE_NUMBER]
- [TRAIN #27] Stripped leading punct: '(0322) 7951857' -> '0322) 7951857' [PHONE_NUMBER]
- [TRAIN #28] Resolved overlap: Kept longer 'Karachi Kings' [SPORTS_TEAM], dropped nested 'Karachi' [CITY] in sentence: "Management of Karachi Kings confirmed the inclusion of two f..."
- [TRAIN #29] Stripped leading punct: '(0313) 7013362' -> '0313) 7013362' [PHONE_NUMBER]
- [TRAIN #30] Stripped leading punct: '(042) 7982241' -> '042) 7982241' [PHONE_NUMBER]
- [TRAIN #31] Stripped leading punct: '(0330) 3456269' -> '0330) 3456269' [PHONE_NUMBER]
- [TRAIN #32] Resolved overlap: Kept longer 'Lahore High Court' [COURT_LEGAL_BODY], dropped nested 'Lahore' [CITY] in sentence: "A division bench of the Lahore High Court heard arguments re..."
- [TRAIN #33] Stripped leading punct: '(091) 9191131' -> '091) 9191131' [PHONE_NUMBER]
- [TRAIN #34] Stripped leading punct: '(081) 9398441' -> '081) 9398441' [PHONE_NUMBER]
- [TRAIN #35] Stripped leading punct: '(0309) 6581590' -> '0309) 6581590' [PHONE_NUMBER]
- [TRAIN #36] Stripped leading punct: '(0320) 9702983' -> '0320) 9702983' [PHONE_NUMBER]
- [TRAIN #37] Stripped leading punct: '(041) 2414808' -> '041) 2414808' [PHONE_NUMBER]
- [TRAIN #38] Resolved overlap: Kept longer 'Lahore High Court' [COURT_LEGAL_BODY], dropped nested 'Lahore' [CITY] in sentence: "In a landmark judgment on Monday, the Lahore High Court uphe..."
- [TRAIN #39] Stripped leading punct: '(۰۴۲) ۴۸۵۹۹۹۲' -> '۰۴۲) ۴۸۵۹۹۹۲' [PHONE_NUMBER]
- [TRAIN #40] Stripped leading punct: '(0324) 4196314' -> '0324) 4196314' [PHONE_NUMBER]
- [TRAIN #41] Stripped leading punct: '(022) 2044906' -> '022) 2044906' [PHONE_NUMBER]
- [TRAIN #42] Stripped leading punct: '(0330) 8706432' -> '0330) 8706432' [PHONE_NUMBER]
- [TRAIN #43] Stripped leading punct: '(0314) 9541056' -> '0314) 9541056' [PHONE_NUMBER]
- [TRAIN #44] Stripped leading punct: '(0322) 1299098' -> '0322) 1299098' [PHONE_NUMBER]
- [TRAIN #45] Stripped leading punct: '(081) 5557052' -> '081) 5557052' [PHONE_NUMBER]
- [TRAIN #46] Stripped leading punct: '(091) 5476257' -> '091) 5476257' [PHONE_NUMBER]
- [TRAIN #47] Stripped leading punct: '(041) 3450300' -> '041) 3450300' [PHONE_NUMBER]
- [TRAIN #48] Stripped leading punct: '(022) 2538024' -> '022) 2538024' [PHONE_NUMBER]
- [TRAIN #49] Stripped leading punct: '(081) 1674975' -> '081) 1674975' [PHONE_NUMBER]
- [TRAIN #50] Stripped leading punct: '(091) 9304320' -> '091) 9304320' [PHONE_NUMBER]

*...and 70 more automatic span alignments.*
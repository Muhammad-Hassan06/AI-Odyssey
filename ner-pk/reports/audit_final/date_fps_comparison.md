# DATE False Positives: Before vs After Strict Rule Hardening

- **Before False Positive Count:** 101
- **After False Positive Count:** 25
- **Net Spurious Matches Eliminated:** 76

## 50 Before False Positives (Eliminated Bare Weekdays & Case-Insensitive Words)

| # | Dev Sent ID | Spurious Extracted String | Sentence Context |
| :-: | :-: | :--- | :--- |
| 1 | dev_113 | `3 فروری 1839` | انگریزوں نے 3 فروری 1839ء کو کراچی شہر پر حملہ کیا اور اس پر قبضہ کر لیا۔... |
| 2 | dev_354 | `اتوار` | پشاور ہائی کورٹ نے مجموعہ تعزیرات پاکستان کے تحت دائر آئینی درخواست کی سماعت اتوار تک ملتو... |
| 3 | dev_358 | `Saturday` | A symposium on modern computing was organized jointly at Aga Khan University in Multan on ... |
| 4 | dev_361 | `Friday` | Candidates may reach out to the admissions office at 03101272597 before Friday afternoon.... |
| 5 | dev_362 | `Wednesday` | In an exciting match on Wednesday, Lahore Qalandars secured victory against their opponent... |
| 6 | dev_363 | `Monday` | Delegates from across the region gathered in Lahore on Monday to participate actively in C... |
| 7 | dev_366 | `اتوار` | انسداد دہشت گردی عدالت نے 26ویں آئینی ترمیم کے تحت دائر آئینی درخواست کی سماعت اتوار تک مل... |
| 8 | dev_368 | `Monday` | The breaking news was telecast prominently across The Express Tribune on Monday evening.... |
| 9 | dev_378 | `Thursday` | Supporters of Pakistan Hockey Team celebrated enthusiastically in Lahore after the thrilli... |
| 10 | dev_386 | `Tuesday` | For verification of public utility services on Tuesday, call 0334 8383027 today.... |
| 11 | dev_389 | `جمعہ` | آغا خان یونیورسٹی میں داخلوں کا باقاعدہ آغاز جمعہ سے کیا جا رہا ہے۔... |
| 12 | dev_392 | `Friday` | Candidates may reach out to the admissions office at 0092 341 1955254 before Friday aftern... |
| 13 | dev_393 | `Thursday` | Delegates from across the region gathered in Rawalpindi on Thursday to participate activel... |
| 14 | dev_396 | `جمعہ` | قومی اسمبلی کا اجلاس جمعہ کو شام ۶ بجے طلب کر لیا گیا ہے۔... |
| 15 | dev_398 | `Monday` | For verification of public utility services on Monday, call 03409186082 today.... |
| 16 | dev_419 | `Friday` | Admissions for the upcoming academic semester opened at LUMS in Karachi on Friday.... |
| 17 | dev_428 | `Monday` | Delegates from across the region gathered in Quetta on Monday to participate actively in P... |
| 18 | dev_448 | `Thursday` | The emergency cabinet meeting commenced at 4:00 PST sharp in Quetta on Thursday.... |
| 19 | dev_454 | `Thursday` | The breaking news was telecast prominently across The Express Tribune on Thursday evening.... |
| 20 | dev_462 | `Friday` | Admissions for the upcoming academic semester opened at NED University in Rawalpindi on Fr... |
| 21 | dev_465 | `Friday` | Proceedings at the assembly adjourned at 1:15 PM following the debate on Friday.... |
| 22 | dev_472 | `Sunday` | A total of 2986 citizens attended the public seminar in Islamabad on Sunday.... |
| 23 | dev_473 | `بدھ` | قومی اسمبلی کا اجلاس بدھ کو شام ۳ بجے طلب کر لیا گیا ہے۔... |
| 24 | dev_474 | `Monday` | Proceedings at the assembly adjourned at 5:15 PM following the debate on Monday.... |
| 25 | dev_477 | `Friday` | Candidates may reach out to the admissions office at (055) 9890570 before Friday afternoon... |
| 26 | dev_484 | `Sunday` | Delegates from across the region gathered in Rawalpindi on Sunday to participate actively ... |
| 27 | dev_485 | `Sunday` | Admissions for the upcoming academic semester opened at IBA Karachi in Lahore on Sunday.... |
| 28 | dev_488 | `Wednesday` | Trading at the exchange concluded smoothly at 5:45 am on Wednesday with heavy turnover.... |
| 29 | dev_501 | `Monday` | In a landmark judgment on Monday, the Accountability Court upheld the enforcement of Code ... |
| 30 | dev_507 | `Tuesday` | Proceedings at the assembly adjourned at 3:00 AM following the debate on Tuesday.... |
| 31 | dev_510 | `Friday` | For verification of public utility services on Friday, call 0335-4866041 today.... |
| 32 | dev_511 | `پیر` | فاسٹ یونیورسٹی میں داخلوں کا باقاعدہ آغاز پیر سے کیا جا رہا ہے۔... |
| 33 | dev_513 | `Thursday` | The emergency cabinet meeting commenced at 12:00 AM sharp in Lahore on Thursday.... |
| 34 | dev_514 | `جمعرات` | قومی اسمبلی کا اجلاس جمعرات کو رات 5 بجے طلب کر لیا گیا ہے۔... |
| 35 | dev_517 | `Thursday` | For verification of public utility services on Thursday, call 0092 305 4709452 today.... |
| 36 | dev_518 | `Saturday` | In a landmark judgment on Saturday, the Federal Shariat Court upheld the enforcement of In... |
| 37 | dev_522 | `Monday` | Delegates from across the region gathered in Rawalpindi on Monday to participate actively ... |
| 38 | dev_525 | `Wednesday` | Trading at the exchange concluded smoothly at 10:30 pm on Wednesday with heavy turnover.... |
| 39 | dev_527 | `Friday` | A total of 3820 citizens attended the public seminar in Peshawar on Friday.... |
| 40 | dev_530 | `Friday` | Candidates may reach out to the admissions office at +92 330 7653215 before Friday afterno... |
| 41 | dev_532 | `Tuesday` | In an exciting match on Tuesday, Islamabad United secured victory against their opponents ... |
| 42 | dev_537 | `Thursday` | Delegates from across the region gathered in Quetta on Thursday to participate actively in... |
| 43 | dev_542 | `Friday` | Candidates may reach out to the admissions office at +92 21 2790897 before Friday afternoo... |
| 44 | dev_545 | `جمعہ` | لاہور ہائی کورٹ نے پیکا ایکٹ کے تحت دائر آئینی درخواست کی سماعت جمعہ تک ملتوی کر دی۔... |
| 45 | dev_550 | `Sunday` | Delegates from across the region gathered in Islamabad on Sunday to participate actively i... |
| 46 | dev_552 | `Saturday` | Supporters of Pakistan Hockey Team celebrated enthusiastically in Faisalabad after the thr... |
| 47 | dev_553 | `Monday` | For verification of public utility services on Monday, call (0314) 9263316 today.... |
| 48 | dev_557 | `Monday` | Proceedings at the assembly adjourned at 3:15 AM following the debate on Monday.... |
| 49 | dev_564 | `Thursday` | Admissions for the upcoming academic semester opened at NED University in Lahore on Thursd... |
| 50 | dev_568 | `Friday` | Candidates may reach out to the admissions office at 0092 317 5471801 before Friday aftern... |

## 50 After False Positives (Remaining Real Calendar Mentions Not Tagged in Ground Truth)

| # | Dev Sent ID | Extracted String | Sentence Context |
| :-: | :-: | :--- | :--- |
| 1 | dev_023 | `March 1982` | Highest rainfall during 24 hours in Quetta is 113 millimetres (4.4 in) which was recorded ... |
| 2 | dev_047 | `March 1949` | Before writing a constitution, a Constituent Assembly passed the Objectives Resolution, on... |
| 3 | dev_059 | `December 1970` | To hold the proposed elections, President Yahya promulgated a Legal Framework Order on 30 ... |
| 4 | dev_083 | `October 2002` | Geo News (Urdu: جیو نیوز) is a Pakistani TV news channel owned by the Jang Media Group, fo... |
| 5 | dev_085 | `October 2002` | Geo TV was the biggest news channel in Pakistan in 2007 and still in 2025.[3][4]  Geo News... |
| 6 | dev_087 | `November 2007` | This has also put Geo TV in numerous conflicts with the Pakistani government".[1]  In Nove... |
| 7 | dev_113 | `3 فروری 1839` | انگریزوں نے 3 فروری 1839ء کو کراچی شہر پر حملہ کیا اور اس پر قبضہ کر لیا۔... |
| 8 | dev_223 | `October 2011` | The Punjab Olympic Association made a similar request in late October 2011 to the provinci... |
| 9 | dev_234 | `April 2004` | The Indian team toured Pakistan for a full series, consisting of three Tests and five ODIs... |
| 10 | dev_238 | `August 2017` | This event brought a halt to international cricket in Pakistan.[2]  International cricket ... |
| 11 | dev_239 | `August 2017` | With that, under heavy security, PCB planned World XI tour to Pakistan for three T20Is.[27... |
| 12 | dev_239 | `March 2009` | With that, under heavy security, PCB planned World XI tour to Pakistan for three T20Is.[27... |
| 13 | dev_282 | `June 2025` | However, according to a World Bank report released in June 2025, around 45% of Pakistan's ... |
| 14 | dev_286 | `July 2008` | New designs of Rs. 5 (July 2008, later replaced by a coin), 10 (May 2006), Rs. 20 (March 2... |
| 15 | dev_286 | `May 2006` | New designs of Rs. 5 (July 2008, later replaced by a coin), 10 (May 2006), Rs. 20 (March 2... |
| 16 | dev_286 | `March 2008` | New designs of Rs. 5 (July 2008, later replaced by a coin), 10 (May 2006), Rs. 20 (March 2... |
| 17 | dev_286 | `July 2008` | New designs of Rs. 5 (July 2008, later replaced by a coin), 10 (May 2006), Rs. 20 (March 2... |
| 18 | dev_286 | `November 2006` | New designs of Rs. 5 (July 2008, later replaced by a coin), 10 (May 2006), Rs. 20 (March 2... |
| 19 | dev_286 | `January 2010` | New designs of Rs. 5 (July 2008, later replaced by a coin), 10 (May 2006), Rs. 20 (March 2... |
| 20 | dev_286 | `February 2007` | New designs of Rs. 5 (July 2008, later replaced by a coin), 10 (May 2006), Rs. 20 (March 2... |
| 21 | dev_286 | `May 2006` | New designs of Rs. 5 (July 2008, later replaced by a coin), 10 (May 2006), Rs. 20 (March 2... |
| 22 | dev_299 | `September 1951` | Meanwhile, KIA, Hyundai, Changan, and Prince DFSK have already commenced productions in Pa... |
| 23 | dev_327 | `July 2017` | The mobile telephone market has expanded many-fold since 2003, reaching a subscriber base ... |
| 24 | dev_874 | `9 March 2022` | The case in point is the intentional BrahMos missile attack on Pakistan on 9 March 2022.... |
| 25 | dev_880 | `May 2025` | Strategic landscape post-2025 Jamil stressed that in the wake of the May 2025 conflict, th... |

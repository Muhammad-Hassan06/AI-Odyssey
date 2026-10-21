with open('src/preannotate.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_block = '''    # 1.6 Common Pakistani Personal Name convention (Muhammad Bilal, Shazia Baig, etc.)
    PAK_FIRST_NAMES = (
        r"Muhammad|Mohammad|Mohd\.?|Syed|Hafiz|Malik|Shazia|Mehwish|Hira|Sana|Komal|"
        r"Maryam|Saad|Junaid|Bilal|Sadia|Danish|Omar|Hamza|Ali|Usman|Zain|Ahmed|Ahmad|"
        r"Fatima|Ayesha|Zahra|Tariq|Asim|Fahad|Kamran|Waqar|Noman|Farhan|Imran|Babar|"
        r"Shaheen|Rizwan|Haris|Naseem|Fakhar|Shadab|Iftikhar|Imad|Sarfaraz|Shoaib|Shahid|"
        r"Misbah|Younis|Inzamam|Wasim|Javed|Saeed|Azhar|Shan|Abdullah|Saim|Tahir|Naveed|"
        r"Kashif|Rashid|Sohail|Adnan|Salman|Rehan|Zeeshan|Arsalan|Ahsan|Umair|Waleed|"
        r"Atif|Shahzad|Shahbaz|Nawaz|Asif|Arshad"
    )
    PAK_SURNAMES = (
        r"Baig|Ansari|Javed|Rehman|Rahman|Ahmed|Ahmad|Farooqui|Farooq|Siddiqui|Ghani|"
        r"Malik|Butt|Shaikh|Sheikh|Khan|Chaudhry|Choudhary|Qureshi|Raza|Shah|Memon|"
        r"Abbasi|Bhatti|Mirza|Niazi|Bajwa|Dar|Lodhi|Gillani|Gilani|Tareen|Tarar|"
        r"Warraich|Zardari|Sharif|Bhutto|Iqbal|Jinnah|Akram|Younis|Afridi|Nadeem|Salam|"
        r"Wattoo|Leghari|Mazari|Mengal|Bugti|Marri|Achakzai|Kakar|Durrani|Yousafzai|Shinwari|Khattak"
    )
    PAK_NAME_PATTERN = re.compile(
        rf"\\b(?:{PAK_FIRST_NAMES})\\s+(?:{PAK_SURNAMES})\\b"
    )
    for m in PAK_NAME_PATTERN.finditer(text):
        full_name = m.group(0).strip()
        candidates.append({
            "text": full_name,
            "start": m.start(),
            "end": m.end(),
            "label": "PERSON",
            "priority": 10
        })

    # 1.7 Sports Match Context: teams competing in cricket/football matches are SPORTS_TEAM
    SPORTS_MATCH_PAT = re.compile(
        r"\\b([A-Z][a-zA-Z\\s]+?)\\s+(?:defeated|beat|won against|lost to|played against)\\s+([A-Z][a-zA-Z\\s]+?)\\s+by\\s+\\d+\\s+(?:runs|wickets|goals|points)\\b"
    )
    for m in SPORTS_MATCH_PAT.finditer(text):
        team1 = m.group(1).strip()
        team2 = m.group(2).strip()
        candidates.append({
            "text": team1,
            "start": m.start(1),
            "end": m.start(1) + len(team1),
            "label": "SPORTS_TEAM",
            "priority": 11
        })
        candidates.append({
            "text": team2,
            "start": m.start(2),
            "end": m.start(2) + len(team2),
            "label": "SPORTS_TEAM",
            "priority": 11
        })
'''

# Replace lines 291 to 356 (0-indexed 291 to 356)
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if "# 1.6 Common Pakistani Personal Name" in line:
        start_idx = i
    if "# 2. Gazetteer entities with OCR/typo" in line:
        end_idx = i

assert start_idx is not None and end_idx is not None, f"indices: {start_idx}, {end_idx}"
lines = lines[:start_idx] + [new_block + "\n"] + lines[end_idx:]

with open('src/preannotate.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("SUCCESS: cleaned preannotate.py lines")

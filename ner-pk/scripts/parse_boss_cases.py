import re
import json

import os
import re
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_path = os.path.join(base_dir, 'tests', 'boss_15_cases_raw.txt')

with open(raw_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find Test Case #X and its command & expected entities
raw_cases = re.findall(r'(Test Case #\d+[\s\S]*?(?=Test Case #|\Z))', content)
print(f'Found {len(raw_cases)} raw cases')

cases = []
for rc in raw_cases:
    # extract title
    title_match = re.search(r'(Test Case #\d+[^\n\r]*)', rc)
    title = title_match.group(1).strip() if title_match else 'Unknown'
    
    # extract text: look for --text "..." or --text '...'
    text_match = re.search(r'--text\s+"([^"]+)"', rc)
    if not text_match:
        text_match = re.search(r"--text\s+'([^']+)'", rc)
    
    text = text_match.group(1) if text_match else ''
    
    # extract expected
    exp_match = re.search(r'Expected Entities\s*\([^)]*\):\s*([^\n\r]+(?:\n[^\n\r]+)*?)(?=\n\s*(?:Brutal Trap|PowerShell|\Z))', rc)
    exp_str = exp_match.group(1).strip() if exp_match else ''
    
    cases.append({
        'title': title,
        'text': text,
        'expected_str': exp_str
    })

print(f'Parsed {len(cases)} cases successfully:')
json_path = os.path.join(base_dir, 'tests', 'parsed_boss_cases.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(cases, f, indent=2, ensure_ascii=False)

print(f'Successfully parsed and saved {len(cases)} cases to {json_path}')

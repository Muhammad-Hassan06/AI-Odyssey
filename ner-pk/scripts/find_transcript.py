import json

trans_path = 'C:/Users/M Wasay/.gemini/antigravity/brain/f9fdbe72-70ca-42b5-8b4e-c4a32ebfb0e0/.system_generated/logs/transcript.jsonl'
with open(trans_path, encoding='utf-8') as f:
    for idx, line in enumerate(f):
        item = json.loads(line)
        content = item.get('content', '')
        if 'Part 2' in content or 'blueprint' in content or 'hidden' in content.lower():
            print(f"Step {idx} ({item.get('type')}) - {content[content.find('Part 2'):content.find('Part 2')+1500]}")

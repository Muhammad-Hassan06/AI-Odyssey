import json

full_path = 'C:/Users/M Wasay/.gemini/antigravity/brain/f9fdbe72-70ca-42b5-8b4e-c4a32ebfb0e0/.system_generated/logs/transcript_full.jsonl'
with open(full_path, encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if idx == 2055:
            item = json.loads(line)
            content = item.get('content', '')
            p2 = content.find('Part 2:')
            if p2 != -1:
                print(content[p2:p2+3000])
            else:
                print("Part 2 not found, first 1000 chars:", content[:1000])
            break

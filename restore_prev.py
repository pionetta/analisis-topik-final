import json
import re

transcript_path = r"C:\Users\hp\.gemini\antigravity-ide\brain\8f6bcadc-603c-4f8e-90af-73a1f7a95e1e\.system_generated\logs\transcript_full.jsonl"
output_path = r"C:\Users\hp\OneDrive\Documents\Arstywn\Aplikasi\Analisis Topik 6\frontend\src\pages\Analysis.jsx"

content_parts = {}
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'Analysis.jsx' not in line:
            continue
        try:
            data = json.loads(line)
        except:
            continue
            
        if data.get('type') == 'VIEW_FILE' and 'Analysis.jsx' in data.get('content', ''):
            content = data['content']
            if 'Showing lines' in content:
                match = re.search(r'Showing lines (\d+) to (\d+)', content)
                if match:
                    start_line = int(match.group(1))
                    end_line = int(match.group(2))
                    lines_text = content.split('and leading space.\n')[-1]
                    if 'The above content does NOT show' in lines_text:
                        lines_text = lines_text.split('\nThe above content does NOT show')[0]
                    elif 'The above content shows the entire' in lines_text:
                        lines_text = lines_text.split('\nThe above content shows the entire')[0]
                    clean_lines = []
                    for l in lines_text.split('\n'):
                        prefix = re.match(r'^\d+: (.*)', l)
                        if prefix:
                            clean_lines.append(prefix.group(1))
                        else:
                            clean_lines.append(l)
                    content_parts[(start_line, end_line)] = clean_lines

print(f"Found parts: {list(content_parts.keys())}")

full_lines = []
max_line = max([end for start, end in content_parts.keys()]) if content_parts else 0

if max_line > 0:
    full_lines = [""] * max_line
    for (start, end), lines in content_parts.items():
        for i, line in enumerate(lines):
            idx = start - 1 + i
            if idx < max_line:
                full_lines[idx] = line

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(full_lines))
    print(f"Reconstructed Analysis.jsx from previous convo with {len(full_lines)} lines.")
else:
    print("Could not find content parts in previous convo.")

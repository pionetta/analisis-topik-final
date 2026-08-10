import json
import os

session_dir = r"c:\Users\hp\OneDrive\Documents\Arstywn\Aplikasi\Analisis Topik 6\backend\uploads"
files = [f for f in os.listdir(session_dir) if f.startswith('session_') and f.endswith('.json')]
if files:
    latest_file = max([os.path.join(session_dir, f) for f in files], key=os.path.getmtime)
    print(f"Checking session file: {latest_file}")
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    tokens_all = data.get('processed_tokens_all', {})
    if tokens_all:
        print("Unigram docs count:", len(tokens_all.get('unigram', [])))
        
        uni_set = set(w for d in tokens_all.get('unigram', []) for w in d)
        bi_set = set(w for d in tokens_all.get('bigram', []) for w in d)
        tri_set = set(w for d in tokens_all.get('trigram', []) for w in d)
        
        bigrams_only = [w for w in bi_set if '_' in w]
        trigrams_only = [w for w in tri_set if w.count('_') >= 2]
        
        print(f"Unique words in Unigram: {len(uni_set)}")
        print(f"Unique words in Bigram: {len(bi_set)} | Bigram phrases: {len(bigrams_only)}")
        print(f"Unique words in Trigram: {len(tri_set)} | Trigram phrases: {len(trigrams_only)}")
        
        if bigrams_only:
            print("Sample Bigrams:", bigrams_only[:10])
        if trigrams_only:
            print("Sample Trigrams:", trigrams_only[:10])
    else:
        print("No tokens found")
else:
    print("No session files found")

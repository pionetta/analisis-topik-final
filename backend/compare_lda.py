import json
import os
import gensim.corpora as corpora
from gensim.models import LdaModel

session_dir = r"c:\Users\hp\OneDrive\Documents\Arstywn\Aplikasi\Analisis Topik 6\backend\uploads"
files = [f for f in os.listdir(session_dir) if f.startswith('session_') and f.endswith('.json')]
latest_file = max([os.path.join(session_dir, f) for f in files], key=os.path.getmtime)
print(f"Using session: {latest_file}")
with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    
tokens_all = data.get('processed_tokens_all', {})

for mode in ['unigram', 'bigram', 'trigram']:
    tokens = tokens_all.get(mode, [])
    id2word = corpora.Dictionary(tokens)
    id2word.filter_extremes(no_below=2, no_above=0.75)
    corpus = [id2word.doc2bow(text) for text in tokens]
    
    print(f"\nTraining LDA for {mode}...")
    model = LdaModel(
        corpus=corpus,
        id2word=id2word,
        num_topics=3,
        random_state=42,
        passes=10,
        iterations=100
    )
    
    print(f"Top words for {mode}:")
    for idx, topic in model.show_topics(num_topics=3, num_words=10, formatted=False):
        print(f"Topic {idx+1}: {[w for w, _ in topic]}")

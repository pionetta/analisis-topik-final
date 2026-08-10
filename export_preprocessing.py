import os
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim.models.phrases import Phrases, Phraser

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)

def process_dataset(filepath):
    filename = os.path.basename(filepath)
    print(f"Memproses {filename}...")
    
    try:
        df = pd.read_csv(filepath)
        # Ambil kolom review_text, atau kolom kedua jika tidak ada
        if 'review_text' in df.columns:
            raw_texts = df['review_text'].dropna().astype(str).tolist()
        else:
            raw_texts = df.iloc[:, 1].dropna().astype(str).tolist()
    except Exception as e:
        print(f"Error membaca {filename}: {e}")
        return None
        
    stop_words = set(stopwords.words('english'))
    negation_words = {"not", "no", "never", "cannot", "without", "neither", "nor"}
    stop_words = stop_words - negation_words
    
    custom_stops = {
        "movie", "film", "movies", "films", "one", "like", "time", "even", 
        "much", "really", "also", "ever", "many", "way", "made", "people", 
        "say", "still", "think", "two", "every", "make", "could", "something", 
        "get", "never", "see", "seen", "watch", "story", "plot", "character", 
        "characters", "best", "great", "good", "well", "love", "better", "end", "world",
        "just", "feel", "little", "makes", "know", "times",
        "quite", "going", "real", "right", "thought",
        "want", "point", "thing", "things", "anything", "everything", "nothing",
        "actually", "sure", "different", "definitely", "find", "found",
        "first", "last", "another", "whole", "second", "always", "never",
        "year", "years", "day", "days", "time", "hour", "hours", "minute", "minutes",
        "scene", "scenes", "part", "parts", "moment", "moments",
        "actor", "actors", "actress", "action", "role", "roles", "performance", "performances",
        "director", "directing", "direction", "cinema", "screen", "theater", "theatre",
        "masterpiece", "masterpieces", "classic", "work", "job",
        "view", "viewer", "viewers", "audience", "watching", "watched",
        "overall", "review", "reviews", "rating", "star", "stars", "someone",
        "already", "around", "back", "come", "comes", "take", "takes", "give", "gives",
        "look", "looks", "looking", "need", "needs", "works"
    }

    clean_filename = re.sub(r'^\d+_', '', filename)
    clean_filename = re.sub(r'_\d{4}\.csv$', '', clean_filename)
    clean_filename = clean_filename.replace('.csv', '').replace('_', ' ')
    
    title_words = set(clean_filename.lower().split())
    custom_stops = custom_stops.union(title_words)
    
    filename_lower = clean_filename.lower()
    if "dark knight" in filename_lower or "batman" in filename_lower:
        custom_stops.update({"batman", "nolan", "joker", "bruce", "wayne", "heath", "ledger", "gotham", "dark", "knight"})
    elif "lord of the rings" in filename_lower:
        custom_stops.update({"frodo", "ring", "gandalf", "sam", "peter", "jackson", "hobbit", "king", "lord", "rings", "return"})
    elif "avengers" in filename_lower or "endgame" in filename_lower:
        custom_stops.update({"marvel", "avenger", "avengers", "thanos", "stark", "iron", "man", "tony", "cap", "captain", "america", "endgame", "infinity", "war"})
    elif "spider-man" in filename_lower or "spider man" in filename_lower:
        custom_stops.update({"spider", "man", "spiderman", "peter", "parker", "miles", "morales", "verse", "into"})
    elif "interstellar" in filename_lower:
        custom_stops.update({"space", "cooper", "murph", "nolan", "interstellar"})
    elif "parasite" in filename_lower:
        custom_stops.update({"korean", "family", "bong", "joon", "ho", "house", "parasite"})
    elif "coco" in filename_lower:
        custom_stops.update({"pixar", "miguel", "music", "disney", "mexico", "family", "coco"})
    elif "toy story" in filename_lower:
        custom_stops.update({"pixar", "toy", "toys", "woody", "buzz", "andy", "story"})
    elif "wall-e" in filename_lower:
        custom_stops.update({"pixar", "wall", "eve", "robot", "earth"})
    elif "your name" in filename_lower:
        custom_stops.update({"anime", "mitsuha", "taki", "body", "swap", "shinkai", "name"})
        
    stop_words = stop_words.union(custom_stops)
    
    synonyms = {
        "film": "movie",
        "picture": "movie",
        "epic": "masterpiece",
        "ending": "conclusion"
    }

    valid_original = []
    processed_tokens_temp = []
    step_clean_list = []
    
    for text in raw_texts:
        text_lower = text.lower()
        for word, replacement in synonyms.items():
            text_lower = re.sub(rf'\b{word}\b', replacement, text_lower)
            
        text_elong = re.sub(r'(.)\1{2,}', r'\1\1', text_lower)
        text_clean = re.sub(r'[^a-z\s]', ' ', text_elong)
        text_clean = re.sub(r'\s+', ' ', text_clean).strip()
        
        tokens = word_tokenize(text_clean)
        
        tokens_negation = []
        skip_next = False
        for i in range(len(tokens)):
            if skip_next:
                skip_next = False
                continue
            if tokens[i] in negation_words and i + 1 < len(tokens):
                tokens_negation.append(tokens[i] + "_" + tokens[i + 1])
                skip_next = True
            else:
                tokens_negation.append(tokens[i])
                
        tokens_stopword = [word for word in tokens_negation if word not in stop_words and len(word) > 2]
        
        # We skip lemmatization here for speed in the export, or we can add it if needed.
        # But to be completely accurate, let's just use what's here.
        if len(tokens_stopword) >= 3:
            valid_original.append(text)
            step_clean_list.append(" ".join(tokens_stopword))
            processed_tokens_temp.append(tokens_stopword)
            
    unigram = processed_tokens_temp
    
    bigram = Phrases(processed_tokens_temp, min_count=2, threshold=5)
    bigram_mod = Phraser(bigram)
    bigram_res = [list(bigram_mod[doc]) for doc in processed_tokens_temp]
    
    total_docs_raw = len(raw_texts)
    total_docs_valid = len(processed_tokens_temp)
    total_dropped = total_docs_raw - total_docs_valid
    all_tokens_flat = [tok for doc in bigram_res for tok in doc]
    vocab_size = len(set(all_tokens_flat))
    
    samples = []
    for i in range(min(10, total_docs_valid)):
        samples.append({
            'original': valid_original[i],
            'cleaned': step_clean_list[i],
            'unigram': ", ".join(unigram[i]),
            'bigram': ", ".join(bigram_res[i])
        })
        
    return {
        'title': clean_filename,
        'stats': {
            'total_raw': total_docs_raw,
            'total_valid': total_docs_valid,
            'dropped': total_dropped,
            'vocab_size': vocab_size
        },
        'samples': samples
    }

def generate_html_report(results):
    html = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Laporan Hasil Preprocessing Dataset</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 20px; }
            .container { max-width: 1400px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h1 { text-align: center; color: #2c3e50; margin-bottom: 5px; }
            h2 { color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 5px; margin-top: 40px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px; table-layout: fixed; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; word-wrap: break-word; vertical-align: top; }
            th { background-color: #f8f9fa; color: #333; font-weight: bold; }
            td:nth-child(1) { width: 35%; }
            td:nth-child(2) { width: 25%; }
            td:nth-child(3) { width: 20%; }
            td:nth-child(4) { width: 20%; }
            .stats-box { background: #eef2f5; padding: 15px; border-radius: 6px; display: flex; gap: 20px; margin-bottom: 15px; }
            .stat-item { flex: 1; text-align: center; }
            .stat-value { font-size: 20px; font-weight: bold; color: #2c3e50; }
            .stat-label { font-size: 12px; color: #7f8c8d; }
            .print-btn { display: block; width: 200px; margin: 20px auto; padding: 12px; background: #2980b9; color: #fff; text-align: center; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
            @media print {
                .print-btn { display: none; }
                body { background: #fff; padding: 0; }
                .container { box-shadow: none; padding: 0; max-width: 100%; }
                .page-break { page-break-before: always; }
                th, td { padding: 6px; font-size: 10px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Laporan Hasil Preprocessing Dataset</h1>
            <p style="text-align: center; color: #7f8c8d;">Dokumen ini memuat statistik cleansing dan sampel pembentukan token (N-Gram) untuk setiap dataset film.</p>
            <button class="print-btn" onclick="window.print()">Simpan sebagai PDF</button>
    """
    
    first = True
    for res in sorted(results, key=lambda x: x['title']):
        if not first:
            html += '<div class="page-break"></div>'
        first = False
        
        html += f'<h2>Dataset: {res["title"].upper()}</h2>'
        
        # Statistics
        stats = res['stats']
        html += f"""
        <div class="stats-box">
            <div class="stat-item"><div class="stat-value">{stats['total_raw']}</div><div class="stat-label">Total Ulasan Awal</div></div>
            <div class="stat-item"><div class="stat-value" style="color: #c0392b;">{stats['dropped']}</div><div class="stat-label">Ulasan Dihapus (Kosong/Terlalu Pendek)</div></div>
            <div class="stat-item"><div class="stat-value" style="color: #27ae60;">{stats['total_valid']}</div><div class="stat-label">Total Ulasan Valid</div></div>
            <div class="stat-item"><div class="stat-value">{stats['vocab_size']}</div><div class="stat-label">Ukuran Kosakata (Vocabulary Size)</div></div>
        </div>
        """
        
        # Samples Table
        html += '<table>'
        html += '<thead><tr><th>Teks Asli (Original)</th><th>Setelah Cleansing & Stopword</th><th>Mode Unigram (1 Kata)</th><th>Mode Bigram (2 Kata)</th></tr></thead>'
        html += '<tbody>'
        for s in res['samples']:
            html += '<tr>'
            html += f'<td>{s["original"]}</td>'
            html += f'<td><span style="color: #7f8c8d;">{s["cleaned"]}</span></td>'
            html += f'<td><span style="color: #2980b9;">{s["unigram"]}</span></td>'
            html += f'<td><span style="color: #8e44ad; font-weight: bold;">{s["bigram"]}</span></td>'
            html += '</tr>'
        html += '</tbody></table>'
        
    html += """
        </div>
    </body>
    </html>
    """
    
    with open('Laporan_Preprocessing.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Berhasil membuat Laporan_Preprocessing.html")

if __name__ == '__main__':
    dataset_dir = 'dataset'
    if not os.path.exists(dataset_dir):
        print(f"Folder {dataset_dir} tidak ditemukan.")
        exit(1)
        
    all_results = []
    for file in os.listdir(dataset_dir):
        if file.endswith('.csv'):
            filepath = os.path.join(dataset_dir, file)
            res = process_dataset(filepath)
            if res:
                all_results.append(res)
                
    if all_results:
        generate_html_report(all_results)
    else:
        print("Tidak ada dataset yang berhasil diproses.")

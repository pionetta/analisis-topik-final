import os
import re
import pandas as pd
from flask import Blueprint, request, jsonify
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim.models.phrases import Phrases, Phraser
from services.session_service import UPLOAD_FOLDER, save_session

preprocess_bp = Blueprint('preprocess', __name__)

def get_json_data():
    return request.get_json(silent=True) or {}

@preprocess_bp.route('/preprocess', methods=['POST'])
def preprocess():
    data        = get_json_data()
    column_name = data.get('column')
    filename    = data.get('filename')
    if not filename or not column_name:
        return jsonify({"error": "Filename atau kolom tidak valid."}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File tidak ditemukan di server. Silakan unggah ulang."}), 404

    try:
        df        = pd.read_csv(filepath)
        raw_texts = df[column_name].dropna().astype(str).tolist()

        # Inisialisasi Stopwords NLTK
        stop_words = set(stopwords.words('english'))

        # Amankan kata negasi agar tidak dihapus oleh Stopwords
        negation_words = {"not", "no", "never", "cannot", "without", "neither", "nor"}
        stop_words     = stop_words - negation_words

        # Ekstensi Stopwords Khusus (Diperluas untuk Meningkatkan Coherence Score)
        custom_stops = {
            # Kata generik ulasan & domain film
            "movie", "film", "movies", "films", "one", "like", "time", "even", 
            "much", "really", "also", "ever", "many", "way", "made", "people", 
            "say", "still", "think", "two", "every", "make", "could", "something", 
            "get", "never", "see", "seen", "watch", "story", "plot", "character", 
            "characters", "best", "great", "good", "well", "love", "better", "end", "world",
            
            # Kata pengisi ulasan tambahan (Filler & Evaluation Words)
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

        # Tambahkan kata-kata dari judul file (tanpa tahun dan ekstensi) sebagai stopwords
        clean_filename = re.sub(r'^\d+_', '', filename) # hapus awalan angka
        clean_filename = re.sub(r'_\d{4}\.csv$', '', clean_filename) # hapus tahun dan .csv
        clean_filename = clean_filename.replace('.csv', '').replace('_', ' ')
        
        title_words = set(clean_filename.lower().split())
        custom_stops = custom_stops.union(title_words)
        
        # Hardcoded stopwords khusus untuk masing-masing film
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

        lemmatizer = WordNetLemmatizer()

        valid_original        = []
        processed_tokens_temp = []
        step_original         = []
        step_casefolding      = []
        step_cleansing        = []
        step_stopword         = []
        step_lemmatization    = []

        # Synonym Mapping
        synonyms = {
            "film": "movie",
            "picture": "movie",
            "epic": "masterpiece",
            "ending": "conclusion"
        }

        for text in raw_texts:
            # 1. Case Folding & Synonym Replacement
            text_lower = text.lower()
            for word, replacement in synonyms.items():
                text_lower = re.sub(rf'\b{word}\b', replacement, text_lower)

            # 2. Normalisasi Elongasi ("loooove" -> "loove")
            text_elong = re.sub(r'(.)\1{2,}', r'\1\1', text_lower)

            # 3. Cleansing
            text_clean = re.sub(r'[^a-z\s]', ' ', text_elong)
            text_clean = re.sub(r'\s+', ' ', text_clean).strip()

            # 4. Tokenisasi
            tokens = word_tokenize(text_clean)

            # 5. Penanganan Negasi
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

            # 6. Hapus Stopwords & Filter Panjang Kata (>=4 huruf)
            tokens_no_stop = [w for w in tokens_negation if w not in stop_words and len(w) > 3]

            # 7. POS Tagging
            pos_tags = nltk.pos_tag(tokens_no_stop)

            # 8. Filter hanya Noun & Adjective
            allowed_pos = {'NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS'}
            tokens_filtered = [word for word, tag in pos_tags if tag in allowed_pos]

            # 9. Lemmatization
            tokens_lemma = [lemmatizer.lemmatize(w) for w in tokens_filtered]

            # Filter dokumen yang terlalu pendek (< 4 kata bermakna)
            if tokens_lemma and len(tokens_lemma) >= 4:
                valid_original.append(text)
                processed_tokens_temp.append(tokens_lemma)

                if len(step_original) < 5:
                    step_original.append(text)
                    step_casefolding.append(text_lower)
                    step_cleansing.append(text_clean)
                    step_stopword.append(" ".join(tokens_filtered))
                    step_lemmatization.append(" ".join(tokens_lemma))

        # N-Gram Detection (Run All 3 Modes)
        processed_tokens_all = {}
        
        # Unigram
        processed_tokens_all['unigram'] = processed_tokens_temp
        
        # Bigram
        bigram     = Phrases(processed_tokens_temp, min_count=2, threshold=5)
        bigram_mod = Phraser(bigram)
        processed_tokens_all['bigram'] = [list(bigram_mod[doc]) for doc in processed_tokens_temp]
        
        # Trigram removed as requested
        
        # Use bigram as default for stats preview
        processed_tokens = processed_tokens_all['bigram']

        # ── Statistik Preprocessing ──────────────────────────────
        total_docs_raw   = len(raw_texts)
        total_docs_valid = len(processed_tokens)
        total_dropped    = total_docs_raw - total_docs_valid
        all_tokens_flat  = [tok for doc in processed_tokens for tok in doc]
        vocab_size       = len(set(all_tokens_flat))
        total_tokens     = len(all_tokens_flat)
        doc_lengths      = [len(doc) for doc in processed_tokens]
        avg_tokens       = round(sum(doc_lengths) / len(doc_lengths), 1) if doc_lengths else 0
        sorted_lengths   = sorted(doc_lengths)
        mid              = len(sorted_lengths) // 2
        median_tokens    = sorted_lengths[mid] if sorted_lengths else 0
        # ──────────────────────────────────────────────────────────

        save_session(filename, {
            "processed_tokens_all": processed_tokens_all,
            "original_text": valid_original
        })

        return jsonify({
            "status": "success",
            "data": {
                "original":       step_original,
                "case_folding":   step_casefolding,
                "cleansing":      step_cleansing,
                "stopword":       step_stopword,
                "lemmatization":  step_lemmatization
            },
            "stats": {
                "total_docs_raw":   total_docs_raw,
                "total_docs_valid": total_docs_valid,
                "total_dropped":    total_dropped,
                "vocab_size":       vocab_size,
                "total_tokens":     total_tokens,
                "avg_tokens":       avg_tokens,
                "median_tokens":    median_tokens
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

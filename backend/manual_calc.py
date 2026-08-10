import numpy as np
from itertools import combinations

def extract_manual_calc_data(model, id2word, corpus, clean_tokens, topic_id=0, topn=5, window_size=110):
    # --- 1. Top-N kata topik terpilih ---
    top_words = model.show_topic(topic_id, topn=topn)
    words = [w for w, prob in top_words]
    print(f"Top {topn} words untuk topik {topic_id}:", words)

    # --- 2. Sliding window co-occurrence (basis untuk c_v / NPMI) ---
    word_window_count = {w: 0 for w in words}
    pair_window_count = {p: 0 for p in combinations(words, 2)}
    total_windows = 0

    for doc in clean_tokens:
        # Jika panjang doc < window_size, kita set maksimal start agar minimal iterasi 1 kali
        max_start = max(1, len(doc) - window_size + 1)
        for start in range(max_start):
            window = set(doc[start:start + window_size])
            total_windows += 1
            for w in words:
                if w in window:
                    word_window_count[w] += 1
            # Dictionary iterasi keys secara default
            for w1, w2 in pair_window_count.keys():
                if w1 in window and w2 in window:
                    pair_window_count[(w1, w2)] += 1

    print("\nTotal windows:", total_windows)
    print("Word window count:", word_window_count)
    print("Pair window count:", pair_window_count)

    # --- 3. NPMI antar pasangan kata (confirmation measure c_v) ---
    npmi_scores = {}
    if total_windows > 0:
        for (w1, w2), co in pair_window_count.items():
            p_w1 = word_window_count[w1] / total_windows
            p_w2 = word_window_count[w2] / total_windows
            p_w1w2 = co / total_windows
            
            # Pencegahan division by zero jika suatu kata tidak pernah muncul
            if p_w1w2 == 0 or p_w1 == 0 or p_w2 == 0:
                npmi_scores[(w1, w2)] = -1
            else:
                pmi = np.log(p_w1w2 / (p_w1 * p_w2))
                npmi_scores[(w1, w2)] = pmi / (-np.log(p_w1w2))
    print("\nNPMI scores:", npmi_scores)

    # --- 4. Theta & Phi untuk 1 dokumen contoh (untuk perplexity) ---
    doc_bow = corpus[0]
    # Ambil probabilitas topik untuk dokumen indeks 0
    theta = model.get_document_topics(doc_bow, minimum_probability=0)
    print(f"\nTheta (distribusi topik untuk dokumen ke-0): {theta}")

    phi_topic = dict(model.show_topic(topic_id, topn=20))
    print(f"Phi topik {topic_id} (top 20 words):", phi_topic)

    # --- 5. Log-likelihood per kata (versi optimasi, untuk ilustrasi) ---
    doc_tokens = clean_tokens[0]
    theta_dict = dict(theta)
    log_p_total = 0
    
    # [OPTIMASI] Ambil seluruh matriks distribusi topik-kata sekali jalan
    # model.get_topics() mengembalikan matriks (num_topics, num_words)
    topic_word_matrix = model.get_topics()
    # Normalisasi baris agar jumlah probabilitas kata per topik = 1
    topic_word_matrix = topic_word_matrix / topic_word_matrix.sum(axis=1)[:, np.newaxis]
    
    num_topics = model.num_topics
    
    for w in doc_tokens:
        if w in id2word.token2id:
            w_id = id2word.token2id[w]
            p_w = 0.0
            for k in range(num_topics):
                p_topic_k = theta_dict.get(k, 0.0)
                p_word_given_k = topic_word_matrix[k, w_id]
                p_w += p_topic_k * p_word_given_k
                
            log_p_total += np.log(max(p_w, 1e-12))
            
    if len(doc_tokens) > 0:
        manual_log_perplexity = log_p_total / len(doc_tokens)
        print("\nManual log-perplexity (dokumen 0):", manual_log_perplexity)
        print("Manual perplexity klasik:", np.exp(-manual_log_perplexity))
    else:
        print("\nDokumen ke-0 kosong, tidak bisa menghitung perplexity.")
        manual_log_perplexity = None

    return words, word_window_count, pair_window_count, npmi_scores, theta, phi_topic


if __name__ == "__main__":
    from gensim.corpora import Dictionary
    from gensim.models import LdaModel
    import pandas as pd
    import re

    # 1. Load Data Avengers: Endgame (Ambil 100 ulasan pertama agar cepat)
    print("Loading data Avengers: Endgame...")
    try:
        df = pd.read_csv('../dataset/Avengers_Endgame_2019.csv')
        raw_docs = df['review_text'].dropna().astype(str).tolist()[:100]
    except Exception as e:
        print("Gagal memuat dataset:", e)
        raw_docs = []

    if raw_docs:
        # Tokenisasi sederhana: lowercase & regex alfabet
        clean_tokens = []
        for doc in raw_docs:
            words = re.findall(r'\b[a-z]{3,}\b', doc.lower())
            clean_tokens.append(words)

        # 2. Buat Dictionary & Corpus
        id2word = Dictionary(clean_tokens)
        id2word.filter_extremes(no_below=2, no_above=0.8) # Filter sedikit noise
        corpus = [id2word.doc2bow(text) for text in clean_tokens]

        # 3. Train LDA Model sederhana
        print("Melatih model LDA Avengers (2 Topik)...\n")
        lda_model = LdaModel(corpus=corpus, id2word=id2word, num_topics=2, random_state=42, passes=10)

        # 4. Jalankan kalkulasi manual
        print("=== Menjalankan Kalkulasi Manual (Avengers: Endgame) ===\n")
        extract_manual_calc_data(
            model=lda_model, 
            id2word=id2word, 
            corpus=corpus, 
            clean_tokens=clean_tokens, 
            topic_id=0, 
            topn=5, 
            window_size=110
        )

import gc
import threading
import gensim.corpora as corpora
from gensim.models import LdaModel
from gensim.models.coherencemodel import CoherenceModel
import pyLDAvis
import pyLDAvis.gensim_models

from topic_interpreter import interpret_topic_rule_based
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from academic_interp_db import apply_academic_interpretations
except ImportError:
    # Handle if not found
    def apply_academic_interpretations(payload, mode): return payload

# ==========================================
# BACKGROUND TASK STORE (Moved to SQLite DB)
# ==========================================
from services.db_service import get_task, set_task

def _build_lda_payload(title: str, k: int, tokens, corpus, id2word, raw_texts, mode='unigram'):
    """
    Melatih satu model LDA untuk k topik dan mengembalikan
    (payload_dict, coherence_score_float, perplexity_score_float).
    """
    # [KEAMANAN] Pastikan tokens merupakan list[list[str]] murni yang dapat di-serialize/pickle pada Windows
    clean_tokens = [[str(w) for w in doc] for doc in tokens]

    model = LdaModel(
        corpus=corpus,
        id2word=id2word,
        num_topics=k,
        random_state=42,
        passes=10,
        iterations=100,
        chunksize=100,
        alpha='auto',
        eta='auto'
    )

    coherence_model = CoherenceModel(
        model=model, texts=clean_tokens, dictionary=id2word, coherence='c_v', processes=1
    )
    coh_score  = float(coherence_model.get_coherence())
    perp_score = float(model.log_perplexity(corpus))

    vis      = pyLDAvis.gensim_models.prepare(model, corpus, id2word, sort_topics=False, n_jobs=1)
    vis_html = pyLDAvis.prepared_data_to_html(vis)

    # 1. Hitung distribusi dokumen terlebih dahulu
    doc_distributions = []
    topic_counts = {f"Topik {i+1}": 0 for i in range(k)}

    for i, corp in enumerate(corpus):
        topic_probs = model.get_document_topics(corp)
        if topic_probs:
            dominant = max(topic_probs, key=lambda x: x[1])
            dom_name = f"Topik {dominant[0] + 1}"
            topic_counts[dom_name] += 1
            doc_distributions.append({
                "doc_id":          i + 1,
                "text":            raw_texts[i] if i < len(raw_texts) else "",
                "dominant_topic":  dom_name,
                "probability":     float(dominant[1])
            })

    # 2. Ekstraksi kata kunci per topik & deduplikasi (Filter berdasarkan Mode)
    all_topics_words_weights = []
    raw_topics = list(model.show_topics(num_topics=k, num_words=100, formatted=False))
    for idx, topic in raw_topics:
        seen = set()
        tw = []
        for word, weight in topic:
            cw = str(word).strip()
            
            # FILTER UNTUK BIGRAM (JANGAN TAMPILKAN UNIGRAM)
            if mode == 'bigram' and cw.count('_') != 1:
                continue
                
            if cw not in seen:
                seen.add(cw)
                tw.append((cw, float(weight)))
                if len(tw) >= 10:
                    break
        
        # Jika setelah filter tidak cukup 10 (misal cuma ada 3 bigram), ya sudah biarkan adanya.
        all_topics_words_weights.append(tw)

    # 3. Jalankan interpretasi topik Rule-Based
    topics_data = {}
    for idx in range(k):
        topic_key = f"Topik {idx + 1}"
        topic_ww = all_topics_words_weights[idx]
        
        interp_res = interpret_topic_rule_based(
            topic_index=idx,
            topic_words_weights=topic_ww,
            all_topics_words_weights=all_topics_words_weights,
            document_distributions=doc_distributions
        )

        topics_data[topic_key] = {
            "auto_label":    interp_res["label"],
            "auto_notes":    interp_res["interpretasi"],
            "kategori":      interp_res["kategori"],
            "contoh_ulasan": interp_res["contoh_ulasan"],
            "words":         interp_res["top_words"]
        }

    classified = sum(topic_counts.values())
    overall_distribution = {
        t: round((c / classified) * 100, 2) if classified > 0 else 0
        for t, c in topic_counts.items()
    }

    interpretations = {
        tk: {
            "custom_label":  tv["auto_label"], 
            "notes":         tv["auto_notes"],
            "kategori":      tv["kategori"],
            "contoh_ulasan": tv["contoh_ulasan"]
        }
        for tk, tv in topics_data.items()
    }

    payload = {
        "title":                title,
        "num_topics":           k,
        "coherence_score":      round(coh_score, 4),
        "perplexity_score":     round(perp_score, 4),
        "topics":               topics_data,
        "overall_distribution": overall_distribution,
        "document_distributions": doc_distributions,
        "vis_html":             vis_html,
        "interpretations":      interpretations,
    }
    
    payload = apply_academic_interpretations(payload, mode)

    
    del model, coherence_model, vis
    gc.collect()

    return payload, coh_score, perp_score


def _run_find_optimal_k(task_id, title, min_k, max_k, tokens_all, raw_texts):
    """Dijalankan di thread terpisah. Melatih semua K dari min_k sampai max_k (2-10)."""
    k_list = list(range(min_k, max_k + 1))

    modes = ['unigram', 'bigram']
    total_steps = len(k_list) * len(modes)
    results  = []
    payloads = []

    try:
        step = 0
        for mode in modes:
            tokens = tokens_all.get(mode, [])
            if not tokens:
                continue

            id2word = corpora.Dictionary(tokens)
            id2word.filter_extremes(no_below=2, no_above=0.75)
            
            # Boost n-grams so they can appear in top keywords
            corpus = []
            for text in tokens:
                bow = id2word.doc2bow(text)
                boosted_bow = []
                for word_id, count in bow:
                    word = id2word[word_id]
                    if '_' in word:
                        boosted_bow.append((word_id, count * 5))
                    else:
                        boosted_bow.append((word_id, count))
                corpus.append(boosted_bow)

            for k in k_list:
                task_data = get_task(task_id) or {}
                task_data.update({
                    'progress': step,
                    'total':    total_steps,
                    'current_k': k,
                    'current_mode': mode
                })
                set_task(task_id, task_data)

                payload, coh, perp = _build_lda_payload(title, k, tokens, corpus, id2word, raw_texts, mode=mode)
                payloads.append((payload, mode, k))

                results.append({
                    "k": k,
                    "mode": mode,
                    "score": coh,
                    "perplexity": perp
                })

                step += 1
                task_data = get_task(task_id) or {}
                task_data['progress'] = step
                set_task(task_id, task_data)

        # Pemanasan data: simpan ke memory _tasks
        best = max(results, key=lambda x: x.get('score', 0))
        optimal_k = best['k']
        optimal_mode = best['mode']

        # Cache SEMUA model (Unigram, Bigram untuk K=2..10) ke Database agar tersedia di History
        import sqlite3
        import json
        from services.db_service import DB_PATH
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            for payload, mode, k in payloads:
                db_key = f"{title}_{mode}_k{k}"
                payload["ngram_mode"] = mode
                payload["optimal_k_results"] = results
                cursor.execute(
                    'INSERT OR REPLACE INTO movie_analysis (id_title, result_data) VALUES (?, ?)',
                    (db_key, json.dumps(payload))
                )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error caching to DB: {e}")

        task_data = get_task(task_id) or {}
        task_data['status'] = 'done'
        task_data['results'] = results
        task_data['optimal_k'] = optimal_k
        task_data['optimal_mode'] = optimal_mode
        set_task(task_id, task_data)

    except Exception as e:
        task_data = get_task(task_id) or {}
        task_data['status']  = 'error'
        task_data['message'] = str(e)
        set_task(task_id, task_data)

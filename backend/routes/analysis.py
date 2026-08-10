import json
import uuid
import threading
import gensim.corpora as corpora
from flask import Blueprint, request, jsonify

from services.session_service import load_session
from services.db_service import get_db_connection, get_task, set_task
from services.lda_service import _run_find_optimal_k, _build_lda_payload
from auto_labeler import interpret_topic

analysis_bp = Blueprint('analysis', __name__)

def get_json_data():
    return request.get_json(silent=True) or {}

@analysis_bp.route('/find_optimal_k', methods=['POST'])
def find_optimal_k():
    data     = get_json_data()
    min_k    = max(2, int(data.get('min_k', 2)))
    max_k    = min(10, int(data.get('max_k', 10)))
    filename = data.get('filename')
    title    = data.get('title', 'Dataset_Ulasan').replace(" ", "_")

    if not filename:
        return jsonify({"error": "Sesi terhapus. Silakan unggah dan proses ulang."}), 400

    session_data = load_session(filename)
    tokens_all   = session_data.get('processed_tokens_all', {})
    raw_texts    = session_data.get('original_text', [])

    if not tokens_all:
        return jsonify({"error": "Silakan jalankan preprocessing terlebih dahulu"}), 400

    try:
        task_id = str(uuid.uuid4())
        task_data = {
            'status':    'running',
            'progress':  0,
            'total':     (max_k - min_k + 1) * 3,
            'current_k': min_k,
            'current_mode': 'unigram'
        }
        set_task(task_id, task_data)

        thread = threading.Thread(
            target=_run_find_optimal_k,
            args=(task_id, title, min_k, max_k, tokens_all, raw_texts),
            daemon=True
        )
        thread.start()

        return jsonify({"status": "started", "task_id": task_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis_bp.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = get_task(task_id)

    if not task:
        return jsonify({"error": "Task tidak ditemukan"}), 404

    return jsonify({"status": "success", "data": task})

@analysis_bp.route('/analyze', methods=['POST'])
def analyze():
    data        = get_json_data()
    title       = data.get('title', 'Dataset_Ulasan').replace(" ", "_")
    num_topics  = max(2, min(20, int(data.get('num_topics', 3))))
    mode        = data.get('mode', 'bigram')
    filename    = data.get('filename')

    if not filename:
        return jsonify({"error": "Sesi terhapus. Silakan unggah dan proses ulang."}), 400

    session_data = load_session(filename)
    tokens_all   = session_data.get('processed_tokens_all', {})
    raw_texts    = session_data.get('original_text', [])

    if not tokens_all or mode not in tokens_all:
        return jsonify({"error": "Silakan jalankan preprocessing terlebih dahulu"}), 400

    tokens = tokens_all[mode]

    try:
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

        result_payload, _, _ = _build_lda_payload(title, num_topics, tokens, corpus, id2word, raw_texts, mode=mode)
        result_payload["optimal_k_results"] = data.get('optimal_k_results', None)
        result_payload["ngram_mode"] = mode

        db_key = f"{title}_{mode}_k{num_topics}"
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO movie_analysis (id_title, result_data) VALUES (?, ?)',
            (db_key, json.dumps(result_payload))
        )
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "data": result_payload})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis_bp.route('/auto_interpret_local', methods=['POST'])
def auto_interpret_local():
    data  = get_json_data()
    words = [w['word'] for w in data.get('words', [])]
    try:
        hasil          = interpret_topic(words)
        return jsonify({"status": "success", "label": hasil["label"], "notes": hasil["notes"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import subprocess
import os
from flask import send_file

@analysis_bp.route('/export_all_html', methods=['GET'])
def export_all_html():
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        script_path = os.path.join(root_dir, 'export_pdf.py')
        html_path = os.path.join(root_dir, 'Laporan_Analisis_Lengkap.html')
        subprocess.run(['python', script_path], cwd=root_dir, check=True)
        return send_file(html_path, mimetype='text/html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

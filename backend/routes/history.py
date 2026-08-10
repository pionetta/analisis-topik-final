import json
import csv
import io
from flask import Blueprint, request, jsonify, Response
from werkzeug.utils import secure_filename

from services.db_service import get_db_connection

history_bp = Blueprint('history', __name__)

def get_json_data():
    return request.get_json(silent=True) or {}

@history_bp.route('/update_interpretation', methods=['POST'])
def update_interpretation():
    data         = get_json_data()
    mode         = data.get('mode', 'bigram')
    db_key       = f"{data.get('title')}_{mode}_k{data.get('num_topics')}"
    topic_id     = data.get('topic_id')
    custom_label = data.get('custom_label', '')
    notes        = data.get('notes', '')

    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT result_data FROM movie_analysis WHERE id_title = ?', (db_key,))
        row = cursor.fetchone()
        if row:
            result_data = json.loads(row[0])
            if 'interpretations' not in result_data:
                result_data['interpretations'] = {}
            result_data['interpretations'][topic_id] = {"custom_label": custom_label, "notes": notes}
            cursor.execute(
                'UPDATE movie_analysis SET result_data = ? WHERE id_title = ?',
                (json.dumps(result_data), db_key)
            )
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "data": result_data})

        conn.close()
        return jsonify({"error": "Data analisis belum tersimpan"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@history_bp.route('/saved_movies', methods=['GET'])
def get_saved_movies():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id_title, result_data FROM movie_analysis ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()

        result = []
        for id_title, result_data_json in rows:
            optimal_k = None
            is_empty = False
            try:
                rd = json.loads(result_data_json)
                k_results = rd.get('optimal_k_results')
                if k_results:
                    best = max(k_results, key=lambda x: x.get('score', 0))
                    optimal_k = best.get('k')
                
                # Check if topics meet the minimum threshold of valid words
                topics = rd.get('topics', {})
                total_words = 0
                for t_name, t_data in topics.items():
                    total_words += len(t_data.get('words', []))
                
                # Syarat minimum yang lebih ketat: rata-rata minimal 3 kata kunci valid per topik.
                # Jika K=2, butuh minimal 6 kata total. Jika K=10, butuh minimal 30 kata total.
                k_value = len(topics)
                if k_value > 0 and total_words < (k_value * 3):
                    is_empty = True
            except Exception:
                pass
            result.append({"id_title": id_title, "optimal_k": optimal_k, "is_empty": is_empty})

        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@history_bp.route('/debug_history', methods=['GET'])
def debug_history():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id_title, result_data FROM movie_analysis LIMIT 1')
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"status": "empty"})
            
        is_empty = False
        err = None
        try:
            rd = json.loads(row[1])
        except Exception as e:
            is_empty = True
            err = str(e)
            rd = None
            
        return jsonify({
            "id_title": row[0],
            "type_of_result_data": str(type(row[1])),
            "raw_result_data_start": str(row[1])[:100],
            "json_loads_success": not is_empty,
            "error": err
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@history_bp.route('/saved_movies/<title>', methods=['GET'])
def get_saved_movie_detail(title):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT result_data FROM movie_analysis WHERE id_title = ?', (title,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return jsonify({"status": "success", "data": json.loads(row[0])})
        return jsonify({"error": "Data tidak ditemukan"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@history_bp.route('/delete_movie/<title>', methods=['DELETE'])
def delete_movie(title):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM movie_analysis WHERE id_title = ?', (title,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Data berhasil dihapus"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@history_bp.route('/export_csv/<title>', methods=['GET'])
def export_csv(title):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT result_data FROM movie_analysis WHERE id_title = ?', (title,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "Data tidak ditemukan"}), 404

        result_data      = json.loads(row[0])
        doc_distributions = result_data.get('document_distributions', [])
        interpretations  = result_data.get('interpretations', {})
        topics           = result_data.get('topics', {})

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID Dokumen', 'Teks Ulasan', 'Topik Dominan', 'Label Topik', 'Probabilitas'])

        for doc in doc_distributions:
            dom   = doc.get('dominant_topic', '')
            label = (interpretations.get(dom, {}).get('custom_label')
                     or topics.get(dom, {}).get('auto_label', ''))
            writer.writerow([
                doc.get('doc_id', ''),
                doc.get('text', ''),
                dom,
                label,
                round(doc.get('probability', 0), 4)
            ])

        output.seek(0)
        safe_title = secure_filename(title)
        return Response(
            output.getvalue(),
            mimetype='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': f'attachment; filename="{safe_title}_hasil_analisis.csv"'
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

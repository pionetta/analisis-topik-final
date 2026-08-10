import sqlite3, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import SETELAH topic_interpreter.py diperbarui
from topic_interpreter import interpret_topic_rule_based

DB_PATH = 'database.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT id_title, result_data FROM movie_analysis ORDER BY id_title')
rows = cursor.fetchall()

print(f"Total entri yang akan di-relabel: {len(rows)}")
print("=" * 60)

label_summary = {}

for id_title, result_data_json in rows:
    try:
        rd = json.loads(result_data_json)
        topics          = rd.get('topics', {})
        doc_distributions = rd.get('document_distributions', [])

        if not topics:
            print(f"  SKIP (kosong): {id_title}")
            continue

        # Bangun all_topics_words_weights dari data tersimpan
        sorted_topic_keys = sorted(topics.keys(), key=lambda x: int(x.replace("Topik ", "")))
        all_tww = []
        for t_name in sorted_topic_keys:
            t_data = topics[t_name]
            tww = [(w['word'], float(w['weight'])) for w in t_data.get('words', [])]
            all_tww.append(tww)

        # Re-label setiap topik
        new_topics         = {}
        new_interpretations = {}

        for idx, t_name in enumerate(sorted_topic_keys):
            t_data = topics[t_name]
            tww    = all_tww[idx]

            result = interpret_topic_rule_based(
                topic_index=idx,
                topic_words_weights=tww,
                all_topics_words_weights=all_tww,
                document_distributions=doc_distributions
            )

            new_topics[t_name] = {
                'auto_label':    result['label'],
                'auto_notes':    result['interpretasi'],
                'kategori':      result['kategori'],
                'contoh_ulasan': result['contoh_ulasan'],
                'words':         t_data.get('words', [])
            }
            new_interpretations[t_name] = {
                'custom_label':  result['label'],
                'notes':         result['interpretasi'],
                'kategori':      result['kategori'],
                'contoh_ulasan': result['contoh_ulasan']
            }

        rd['topics']         = new_topics
        rd['interpretations'] = new_interpretations

        cursor.execute(
            'UPDATE movie_analysis SET result_data = ? WHERE id_title = ?',
            (json.dumps(rd), id_title)
        )

        # Ringkasan label
        labels = [v['auto_label'] for v in new_topics.values()]
        label_summary[id_title] = labels
        print(f"  OK: {id_title}")
        for t_name, lbl in zip(sorted_topic_keys, labels):
            print(f"      {t_name} → {lbl}")

    except Exception as e:
        print(f"  ERROR: {id_title} — {e}")

conn.commit()
conn.close()

print()
print("=" * 60)
print("SELESAI! Semua entri berhasil di-relabel.")

import sqlite3, json

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT id_title, result_data FROM movie_analysis WHERE id_title = 'Interstellar_2014_bigram_k7'")
row = cur.fetchone()
data = json.loads(row['result_data'])

topics = data.get('topics', {})
overall_dist = data.get('overall_distribution', {})
doc_dist = data.get('document_distributions', [])

print("overall_distribution:", overall_dist)
print("document_distributions length:", len(doc_dist))
if doc_dist:
    print("doc_dist[0] sample:", doc_dist[0])

print("\n--- DETAIL SETIAP TOPIK ---")
for tname, tdata in topics.items():
    print(f"\n{tname}:")
    print(f"  auto_label: {tdata.get('auto_label')}")
    print(f"  kategori: {tdata.get('kategori')}")
    contoh = tdata.get('contoh_ulasan', [])
    print(f"  contoh_ulasan (count): {len(contoh)}")
    for i, ex in enumerate(contoh[:2]):
        print(f"    [{i}]: {str(ex)[:150]}")
    words = [(w['word'], round(w['weight'],4)) for w in tdata.get('words', [])[:8]]
    print(f"  top8 words: {words}")

conn.close()

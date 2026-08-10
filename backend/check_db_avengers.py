import sqlite3
import json

conn = sqlite3.connect(r"c:\Users\hp\OneDrive\Documents\Arstywn\Aplikasi\Analisis Topik 6\backend\database.db")
cursor = conn.cursor()

cursor.execute('SELECT result_data FROM movie_analysis WHERE id_title=?', ('Avengers_Endgame_2019_unigram_k3',))
uni_data = json.loads(cursor.fetchone()[0])
print("UNIGRAM K=3 TOPICS:")
for t, d in uni_data['topics'].items():
    print(t, [w['word'] for w in d['words'][:10]])

cursor.execute('SELECT result_data FROM movie_analysis WHERE id_title=?', ('Avengers_Endgame_2019_bigram_k3',))
bi_data = json.loads(cursor.fetchone()[0])
print("\nBIGRAM K=3 TOPICS:")
for t, d in bi_data['topics'].items():
    print(t, [w['word'] for w in d['words'][:10]])

cursor.execute('SELECT result_data FROM movie_analysis WHERE id_title=?', ('Avengers_Endgame_2019_trigram_k3',))
tri_data = json.loads(cursor.fetchone()[0])
print("\nTRIGRAM K=3 TOPICS:")
for t, d in tri_data['topics'].items():
    print(t, [w['word'] for w in d['words'][:10]])

conn.close()

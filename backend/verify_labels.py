# -*- coding: utf-8 -*-
import sqlite3, json

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

films = [
    'Avengers_Endgame_2019',
    'Coco_2017',
    'Interstellar_2014',
    'Parasite_2019',
    'Spider-Man_Into_the_Spider-Verse_2018',
    'The_Dark_Knight_2008',
    'The_Lord_of_the_Rings_The_Return_of_the_King_2003',
    'Toy_Story_1995',
    'WALL-E_2008',
    'Your_Name_2016',
]

all_penilaian_umum = 0
all_total = 0

for film in films:
    cursor.execute(
        'SELECT result_data FROM movie_analysis WHERE id_title LIKE ? AND id_title LIKE ?',
        (f'{film}_bigram_%', '%')
    )
    rows = cursor.fetchall()

    best = None
    best_coh = -999
    for row in rows:
        rd = json.loads(row[0])
        coh = rd.get('coherence_score', -999)
        if coh > best_coh:
            best_coh = coh
            best = rd

    if not best:
        continue

    k = best.get('num_topics', '?')
    print(f'\n[{film}] - Bigram K={k}, Coherence={best_coh:.4f}')
    topics = best.get('topics', {})
    for t_name in sorted(topics.keys(), key=lambda x: int(x.replace('Topik ', ''))):
        t_data = topics[t_name]
        label = t_data.get('auto_label', '-')
        kategori = t_data.get('kategori', '-')
        words = [w['word'] for w in t_data.get('words', [])[:5]]
        print(f'  {t_name}: [{label}] | Kategori: {kategori}')
        print(f'    Kata kunci: {words}')
        all_total += 1
        if 'Penilaian Umum' in label:
            all_penilaian_umum += 1

conn.close()
print(f'\n=== RINGKASAN ===')
print(f'Total topik (film bigram terbaik): {all_total}')
print(f'Masih berlabel "Penilaian Umum": {all_penilaian_umum}')
print(f'Berhasil terlabeli spesifik: {all_total - all_penilaian_umum} ({round((all_total-all_penilaian_umum)/all_total*100,1)}%)')

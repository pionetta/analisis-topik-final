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

for film in films:
    # Ambil SEMUA mode bigram untuk mengetahui best K
    cursor.execute(
        "SELECT id_title, result_data FROM movie_analysis WHERE id_title LIKE ?",
        (f'{film}_bigram_%',)
    )
    rows = cursor.fetchall()
    best = None
    best_coh = -999
    for row in rows:
        rd = json.loads(row[1])
        coh = rd.get('coherence_score', -999)
        if coh > best_coh:
            best_coh = coh
            best = (row[0], rd)

    if not best:
        continue

    key, rd = best
    k = rd.get('num_topics')
    perp = rd.get('perplexity_score')
    topics = rd.get('topics', {})
    doc_dist = rd.get('document_distributions', [])
    opt_results = rd.get('optimal_k_results', [])

    # Ambil optimal K per mode
    best_by_mode = {}
    for r in opt_results:
        mode = r.get('mode')
        if mode not in best_by_mode or r.get('score', 0) > best_by_mode[mode]['score']:
            best_by_mode[mode] = r

    print(f"\n{'='*70}")
    print(f"FILM: {film}")
    print(f"{'='*70}")
    print(f"Jumlah Dokumen (ulasan valid): {len(doc_dist)}")
    print(f"K Optimal (Bigram): {k}")
    print(f"Coherence Score (c_v): {best_coh}")
    print(f"Perplexity Score: {perp}")
    print()

    # Tabel coherence per K dan mode (ambil bigram saja)
    bigram_results = [r for r in opt_results if r.get('mode') == 'bigram']
    bigram_results.sort(key=lambda x: x['k'])
    print(f"  Coherence per K (Bigram):")
    for r in bigram_results:
        marker = " <-- OPTIMAL" if r['k'] == k else ""
        print(f"    K={r['k']:2d}  Coherence={r['score']:.4f}  Perplexity={r['perplexity']:.4f}{marker}")

    print()
    print(f"  Topik yang Ditemukan (K={k}, Bigram):")
    sorted_topic_keys = sorted(topics.keys(), key=lambda x: int(x.replace('Topik ', '')))
    for t_name in sorted_topic_keys:
        t_data = topics[t_name]
        label = t_data.get('auto_label', '-')
        kategori = t_data.get('kategori', '-')
        words = [w['word'].replace('_', ' ') for w in t_data.get('words', [])[:8]]
        dist = rd.get('overall_distribution', {}).get(t_name, 0)
        contoh = t_data.get('contoh_ulasan', [])
        print(f"\n    {t_name} | {label}")
        print(f"    Kategori   : {kategori}")
        print(f"    Distribusi : {dist}% dokumen")
        print(f"    Kata Kunci : {', '.join(words)}")
        if contoh:
            print(f"    Contoh     : \"{contoh[0][:120]}...\"")

conn.close()
print(f"\n{'='*70}")
print("SELESAI")

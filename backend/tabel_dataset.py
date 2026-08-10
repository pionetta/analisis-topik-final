# -*- coding: utf-8 -*-
import sqlite3, json

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

films = [
    ('Avengers_Endgame_2019',       'Avengers: Endgame',                   2019, 'MCU / Superhero'),
    ('Coco_2017',                   'Coco',                                2017, 'Animasi / Keluarga'),
    ('Interstellar_2014',           'Interstellar',                        2014, 'Sci-Fi / Drama'),
    ('Parasite_2019',               'Parasite',                            2019, 'Thriller / Drama Sosial'),
    ('Spider-Man_Into_the_Spider-Verse_2018', 'Spider-Man: Into the Spider-Verse', 2018, 'Animasi / Superhero'),
    ('The_Dark_Knight_2008',        'The Dark Knight',                     2008, 'Superhero / Crime'),
    ('The_Lord_of_the_Rings_The_Return_of_the_King_2003', 'LOTR: The Return of the King', 2003, 'Fantasy / Epik'),
    ('Toy_Story_1995',              'Toy Story',                           1995, 'Animasi / Keluarga'),
    ('WALL-E_2008',                 'WALL-E',                              2008, 'Animasi / Sci-Fi'),
    ('Your_Name_2016',              'Your Name (Kimi no Na wa)',            2016, 'Anime / Romance'),
]

results = []

for film_key, film_name, tahun, genre in films:
    cursor.execute(
        "SELECT id_title, result_data FROM movie_analysis WHERE id_title LIKE ?",
        (f'{film_key}_bigram_%',)
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
    k        = rd.get('num_topics')
    perp     = rd.get('perplexity_score')
    topics   = rd.get('topics', {})
    doc_dist = rd.get('document_distributions', [])
    opt_res  = rd.get('optimal_k_results', [])

    # Statistik
    n_docs = len(doc_dist)

    # Coherence per K (bigram only)
    bigram_res = sorted([r for r in opt_res if r.get('mode') == 'bigram'], key=lambda x: x['k'])
    coh_range  = [r['score'] for r in bigram_res]
    coh_min    = round(min(coh_range), 4) if coh_range else '-'
    coh_max    = round(max(coh_range), 4) if coh_range else '-'

    # Topik
    sorted_keys = sorted(topics.keys(), key=lambda x: int(x.replace('Topik ', '')))
    topic_labels = [topics[t].get('auto_label', '-') for t in sorted_keys]
    topic_dist   = [rd.get('overall_distribution', {}).get(t, 0) for t in sorted_keys]
    topic_words  = [
        ', '.join([w['word'].replace('_', ' ') for w in topics[t].get('words', [])[:5]])
        for t in sorted_keys
    ]
    topic_kategori = [topics[t].get('kategori', '-') for t in sorted_keys]

    results.append({
        'film_name': film_name,
        'tahun':     tahun,
        'genre':     genre,
        'n_docs':    n_docs,
        'k':         k,
        'coh':       round(best_coh, 4),
        'perp':      round(perp, 4),
        'coh_min':   coh_min,
        'coh_max':   coh_max,
        'bigram_res':    bigram_res,
        'topic_labels':  topic_labels,
        'topic_dist':    topic_dist,
        'topic_words':   topic_words,
        'topic_kategori':topic_kategori,
        'sorted_keys':   sorted_keys,
        'topics':        topics,
    })

conn.close()

# ── OUTPUT TABEL RINGKASAN ─────────────────────────────────────────────
print("=" * 100)
print("TABEL 1 — RINGKASAN DATASET & HASIL ANALISIS LDA")
print("=" * 100)
header = f"{'No':<3} {'Judul Film':<40} {'Thn':<5} {'Genre':<22} {'N Doc':<7} {'K*':<4} {'Coh (c_v)':<12} {'Perplexity':<12}"
print(header)
print("-" * 100)
for i, r in enumerate(results, 1):
    print(f"{i:<3} {r['film_name']:<40} {r['tahun']:<5} {r['genre']:<22} {r['n_docs']:<7} {r['k']:<4} {r['coh']:<12} {r['perp']:<12}")

print()
print("Keterangan: N Doc = jumlah dokumen valid, K* = jumlah topik optimal, Coh = Coherence Score c_v")

print()
print("=" * 100)
print("TABEL 2 — TOPIK, LABEL, DISTRIBUSI, DAN KATA KUNCI PER FILM")
print("=" * 100)

for r in results:
    print(f"\n[{r['film_name']} ({r['tahun']})] — Bigram, K={r['k']}, Coherence={r['coh']}, Perplexity={r['perp']}")
    print(f"{'Topik':<10} {'Label Kategori':<35} {'% Dok':<8} {'Kata Kunci Utama (5 teratas)'}")
    print("-" * 100)
    for t_name, label, dist, words in zip(r['sorted_keys'], r['topic_labels'], r['topic_dist'], r['topic_words']):
        print(f"{t_name:<10} {label:<35} {str(dist)+'%':<8} {words}")

print()
print("=" * 100)
print("TABEL 3 — COHERENCE SCORE PER K (BIGRAM) PER FILM")
print("=" * 100)

for r in results:
    print(f"\n  [{r['film_name']}]")
    print(f"  {'K':<5} {'Coherence':<12} {'Perplexity':<14} {'Ket'}")
    print(f"  {'-'*50}")
    for row in r['bigram_res']:
        marker = " <- OPTIMAL" if row['k'] == r['k'] else ""
        print(f"  {row['k']:<5} {round(row['score'],4):<12} {round(row['perplexity'],4):<14} {marker}")

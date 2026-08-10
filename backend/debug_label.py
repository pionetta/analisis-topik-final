import sqlite3, json

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Cek sample kata kunci bigram dari beberapa film
test_cases = [
    'Parasite_2019_bigram_k4',
    'The_Dark_Knight_2008_bigram_k9',
    'Interstellar_2014_bigram_k4',
]

for db_key in test_cases:
    cursor.execute('SELECT result_data FROM movie_analysis WHERE id_title = ?', (db_key,))
    row = cursor.fetchone()
    if not row:
        print(f'{db_key}: NOT FOUND')
        continue
    rd = json.loads(row[0])
    print(f'\n=== {db_key} ===')
    for t_name, t_data in rd['topics'].items():
        label = t_data.get('auto_label', '-')
        words = [w['word'] for w in t_data.get('words', [])]
        print(f'  {t_name} -> "{label}" | {words}')

conn.close()

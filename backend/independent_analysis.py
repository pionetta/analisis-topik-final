import sqlite3
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from fpdf import FPDF
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
DATASET_PATH = os.path.join(BASE_DIR, '..', 'dataset', 'Avengers_Endgame_2019.csv')
PDF_PATH = os.path.join(BASE_DIR, '..', 'Perbandingan_Analisis_Topik.pdf')

# ==========================================
# 1. EXTRACT LDA RESULTS FROM DATABASE
# ==========================================
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT result_data FROM movie_analysis WHERE id_title LIKE 'Avengers_Endgame_2019%'")
rows = cursor.fetchall()
conn.close()

best_lda_k = 0
best_lda_score = -9999
best_lda_topics = {}

for row in rows:
    data = json.loads(row[0])
    k = data.get('num_topics')
    score = data.get('coherence_score', -9999)
    
    if score > best_lda_score:
        best_lda_score = score
        best_lda_k = k
        best_lda_topics = data.get('topics', {})

print(f"Best LDA K: {best_lda_k} (Coherence: {best_lda_score})")

# ==========================================
# 2. PERFORM INDEPENDENT NMF ANALYSIS
# ==========================================
print("Membaca dataset dan preprocessing untuk NMF...")
df = pd.read_csv(DATASET_PATH)
df_100 = df.head(100)
raw_texts = df_100['review_text'].dropna().astype(str).tolist()

stop_words = set(stopwords.words('english'))
custom_stops = {"movie", "film", "movies", "films", "one", "like", "time", "even", 
                "much", "really", "also", "ever", "many", "way", "made", "people", 
                "say", "still", "think", "two", "every", "make", "could", "something", 
                "get", "never", "see", "seen", "watch", "story", "plot", "character", 
                "characters", "best", "great", "good", "well", "love", "better", "end", "world",
                "marvel", "avenger", "avengers", "thanos", "stark", "iron", "man", "tony", "cap", "captain", "america", "endgame"}
stop_words = stop_words.union(custom_stops)
lemmatizer = WordNetLemmatizer()

processed_texts = []
for text in raw_texts:
    text_lower = text.lower()
    text_clean = re.sub(r'[^a-z\s]', ' ', text_lower)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()
    tokens = word_tokenize(text_clean)
    tokens_no_stop = [w for w in tokens if w not in stop_words and len(w) > 3]
    pos_tags = nltk.pos_tag(tokens_no_stop)
    allowed_pos = {'NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS'}
    tokens_filtered = [w for w, tag in pos_tags if tag in allowed_pos]
    tokens_lemma = [lemmatizer.lemmatize(w) for w in tokens_filtered]
    processed_texts.append(" ".join(tokens_lemma))

print("Melatih model NMF...")
vectorizer = TfidfVectorizer(max_df=0.95, min_df=2)
tfidf = vectorizer.fit_transform(processed_texts)
feature_names = vectorizer.get_feature_names_out()

nmf = NMF(n_components=best_lda_k, random_state=42, init='nndsvd')
nmf.fit(tfidf)

nmf_topics = {}
for topic_idx, topic in enumerate(nmf.components_):
    top_features_ind = topic.argsort()[:-10 - 1:-1]
    top_features = [feature_names[i] for i in top_features_ind]
    nmf_topics[f"Topik {topic_idx + 1}"] = top_features

# ==========================================
# 3. GENERATE PDF REPORT
# ==========================================
print("Membuat PDF...")
class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Laporan Perbandingan Analisis Topik (LDA vs NMF)', 0, 1, 'C')
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, 'Studi Kasus: Avengers Endgame 2019 (100 Ulasan)', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 11)
        self.multi_cell(0, 7, body)
        self.ln()

pdf = PDF()
pdf.add_page()

intro_text = (
    "Laporan ini membandingkan hasil Topic Modeling dari dua algoritma berbeda pada dataset "
    "Avengers: Endgame (100 ulasan pertama).\n\n"
    "1. Gensim LDA (Aplikasi): Diambil dari hasil aplikasi dengan K terbaik berdasarkan skor Coherence.\n"
    "2. NMF (Independen): Dijalankan menggunakan TF-IDF dan algoritma Non-negative Matrix Factorization "
    "menggunakan library scikit-learn dengan K yang sama."
)
pdf.chapter_title("Pendahuluan")
pdf.chapter_body(intro_text)

pdf.chapter_title(f"Hasil Ekstraksi Topik (K={best_lda_k})")

for i in range(1, best_lda_k + 1):
    topic_key = f"Topik {i}"
    
    lda_data = best_lda_topics.get(topic_key, {})
    lda_words = [w['word'] for w in lda_data.get('words', [])]
    lda_label = lda_data.get('auto_label', 'Unknown')
    
    nmf_words = nmf_topics.get(topic_key, [])
    
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 8, f"Topik {i}", 0, 1)
    
    pdf.set_font('helvetica', 'I', 11)
    pdf.cell(40, 8, "Gensim LDA (Aplikasi):", 0, 0)
    pdf.set_font('helvetica', '', 11)
    pdf.cell(0, 8, ", ".join(lda_words), 0, 1)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(40, 8, "  Auto-Label LDA:", 0, 0)
    pdf.cell(0, 8, lda_label, 0, 1)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font('helvetica', 'I', 11)
    pdf.cell(40, 8, "NMF (Independen):", 0, 0)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 8, ", ".join(nmf_words))
    pdf.ln(5)

pdf.chapter_title("Kesimpulan")
conc_text = (
    "Dari hasil di atas, kita dapat melihat bahwa kedua algoritma (LDA dan NMF) seringkali menangkap "
    "dimensi yang sedikit berbeda.\n"
    "- LDA (Gensim) yang berbasis pada distribusi probabilitas kata sering kali menghasilkan topik "
    "yang lebih luas (broad) atau berfokus pada frekuensi ko-okurensi.\n"
    "- NMF (TF-IDF) cenderung menangkap topik yang lebih spesifik karena pengaruh pembobotan TF-IDF yang "
    "menghukum kata-kata yang terlalu umum."
)
pdf.chapter_body(conc_text)

pdf.output(PDF_PATH)
print(f"PDF berhasil dibuat di: {PDF_PATH}")

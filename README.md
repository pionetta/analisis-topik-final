---
title: Analisis Topik LDA
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# Analisis Topik pada Ulasan Film (LDA)

Aplikasi berbasis **Natural Language Processing** untuk menemukan topik-topik dominan secara otomatis dari dataset ulasan penonton menggunakan **Latent Dirichlet Allocation (LDA)**.

## Fitur Utama

- 📁 **Upload Dataset CSV** — Upload file ulasan film format CSV
- 🧹 **Preprocessing Otomatis** — Case folding, cleansing, stopword removal, lemmatization
- 📊 **Evaluasi K Optimal** — Cari jumlah topik terbaik (K=2–10) via coherence & perplexity
- 🗂️ **History Analisis** — Simpan dan bandingkan hasil antar dataset
- 🗺️ **Peta Topik Interaktif** — Visualisasi pyLDAvis full-screen

## Format Dataset

File CSV dengan minimal satu kolom berisi teks ulasan (bahasa Inggris). Contoh:

| review_text | rating |
|-------------|--------|
| Amazing film with great visuals... | 9 |
| The story felt a bit slow... | 6 |

## Stack Teknologi

- **Frontend**: React 19 + Vite + Recharts
- **Backend**: Flask + Gensim (LDA) + NLTK + pyLDAvis
- **Deploy**: Docker on HuggingFace Spaces

# -*- coding: utf-8 -*-
import os, sys
from app import _build_lda_payload
from gensim import corpora

title = "Test_Movie"
k = 3
raw_texts = [
    "The acting and performance of actors in this movie was incredible and emotional.",
    "The visual effects and animation were stunning and beautiful to look at on screen.",
    "The plot story and ending twist had great narrative climax and writing script."
] * 10

tokens = [t.lower().split() for t in raw_texts]
id2word = corpora.Dictionary(tokens)
corpus = [id2word.doc2bow(t) for t in tokens]

payload, coh, perp = _build_lda_payload(title, k, tokens, corpus, id2word, raw_texts)

print("PAYLOAD TOPIC 1 KEYS:", list(payload['topics']['Topik 1'].keys()))
print("LABEL:", payload['topics']['Topik 1']['auto_label'])
print("KATEGORI:", payload['topics']['Topik 1'].get('kategori'))
print("CONTOH ULASAN:", payload['topics']['Topik 1'].get('contoh_ulasan'))

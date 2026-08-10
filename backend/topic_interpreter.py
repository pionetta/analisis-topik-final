# -*- coding: utf-8 -*-
"""
================================================================================
MODULE: TOPIC INTERPRETER v2 (RULE-BASED METHODOLOGY FOR SKRIPSI)
================================================================================
Modul ini menangani interpretasi topik LDA secara probabilistik dan rule-based 
tanpa memanggil API LLM eksternal, sehingga 100% transparan, teruji, dan 
dapat dipertanggungjawabkan secara metodologis dalam skripsi/karya ilmiah.

LOGIKA METODOLOGI:
1. Distinctiveness Score (TF-IDF Analog antar Topik):
   Menghitung tingkat kekhasan kata w pada topik t dibandingkan dengan k Topik lainnya.
   Formula: Distinctiveness(w, t) = P(w | t) / (mean_{t' != t} P(w | t') + epsilon)

2. Overlap Scoring Kategori Tema:
   Menghitung bobot kesesuaian top-words terhadap kamus taksonomi ulasan film.
   Formula: OverlapScore(Category) = SUM_{i=1..N} (Weight(w_i) / (Rank(i) + 1)) * Match(w_i, Category)

3. Representative Review Selection:
   Mencari dokumen asli ulasan film yang memiliki nilai probabilitas dominan P(t | d) 
   tertinggi untuk topik t.

PERBAIKAN v2:
- Label topik menggunakan nama kategori yang human-readable, bukan kata mentah.
- Kamus taksonomi diperluas dengan kategori baru: penilaian_umum, humor, nostalgia.
- Kalimat interpretasi diperbaiki: evidence string teknis diubah menjadi frasa natural.
- Ditambahkan LABEL_STOPWORDS untuk menyaring kata generik dari label topik.
================================================================================
"""

import re
from typing import List, Dict, Any, Tuple

# ==============================================================================
# 0. STOPWORD KHUSUS LABEL TOPIK
#    Kata-kata ini TIDAK boleh masuk ke label topik meskipun distinctive score-nya
#    tinggi, karena kata ini terlalu generik untuk dijadikan penanda tema.
# ==============================================================================
LABEL_STOPWORDS = {
    # Kata umum film/review
    "movie", "film", "movies", "films", "watch", "watched", "watching",
    "see", "seen", "one", "two", "three", "first", "second", "last",
    "time", "times", "way", "make", "made", "think", "thought",
    "good", "great", "bad", "best", "worst", "better", "well",
    "also", "even", "still", "much", "many", "really", "never",
    "always", "every", "back", "get", "go", "like", "just", "feel",
    "something", "everything", "nothing", "little", "big", "long",
    "new", "old", "full", "real", "true", "right", "found",
    "come", "came", "give", "take", "show", "know", "said",
    "ever", "quite", "rather", "though", "while", "yet",
}

# ==============================================================================
# 1. KAMUS TAKSONOMI KATEGORI & KATA KUNCI PEMICU (RULE-BASED CATEGORIES)
# ==============================================================================
CATEGORY_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "akting": {
        "name": "Akting & Penokohan Karakter",
        "label": "Penampilan Aktor & Karakter",
        "keywords": {
            # ── Unigram ──
            "performance", "actor", "actors", "actress", "character", "characters",
            "role", "roles", "cast", "casting", "acting", "villain", "hero",
            "joker", "batman", "protagonist", "antagonist", "heath", "mcconaughey",
            "bruce", "wayne", "frodo", "gandalf", "portray", "portrayal",
            "dialogue", "delivery", "screen", "presence", "charisma",
            # ── Bigram: Nama Aktor / Sutradara ──
            "christian_bale", "gary_oldman", "michael_caine", "morgan_freeman",
            "maggie_gyllenhaal", "aaron_eckhart", "cillian_murphy", "david_goyer",
            "matthew_mcconaughey", "anne_hathaway", "robert_downey", "russo_brother",
            "sean_astin", "elijah_wood", "viggo_mortensen", "andy_serkis",
            "bernard_hill", "david_wenham", "katie_holmes", "jack_nicholson",
            "tommy_jones", "jake_johnson", "john_lasseter", "andrew_stanton",
            "hayao_miyazaki", "song_kang", "caine_morgan", "eckhart_harvey",
            # ── Bigram: Karakter & Konsep Akting ──
            "hero_villain", "voice_talent", "oscar_worthy", "harvey_dent",
            "human_nature", "load_lifter", "district_attorney", "jack_nicholson",
        },
        "templates": [
            "Pembahasan pada kelompok topik ini mendominasi penilaian audiens terhadap kualitas akting, kharisma penokohan karakter, serta pendalaman peran oleh para pemain utama.",
            "Kelompok ulasan ini menunjukkan apresiasi penonton terhadap keunikan karakter dan daya pikat peran para tokoh yang dimainkan secara memukau.",
            "Topik ini berfokus pada dinamika penokohan dan impresi akting aktor yang menjadi daya tarik utama dan membekas bagi penonton.",
            "Ulasan audiens pada tema ini menyoroti ikatan antar tokoh serta pendalaman emosi karakter yang berhasil menghidupkan suasana cerita."
        ]
    },
    "visual": {
        "name": "Visual & Sinematografi",
        "label": "Kualitas Visual & Sinematografi",
        "keywords": {
            # ── Unigram ──
            "visual", "visuals", "effect", "effects", "cgi", "scene", "scenes",
            "cinematography", "graphics", "graphic", "color", "colours", "colors",
            "animation", "animated", "frame", "shot", "lighting", "design",
            "beauty", "beautiful", "stunning", "gorgeous", "pixar", "spectacular",
            "breathtaking", "imagery", "palette", "texture",
            "direction", "directed", "director", "camera",
            # ── Bigram ──
            "visual_effect", "special_effect", "sound_effect", "animation_style",
            "animation_beautiful", "beautiful_animation", "computer_animation",
            "animation_studio", "cinematic_experience", "attention_detail",
            "sight_gag", "studio_ghibli", "feature_length", "full_length",
        },
        "templates": [
            "Ulasan pada kelompok topik ini berpusat pada keindahan tata visual, kualitas efek khusus CGI, dan keanggunan sinematografi yang memanjakan mata.",
            "Fokus ulasan audiens pada tema ini menyoroti tampilan grafis dan detail estetika visual yang memberikan pengalaman menonton yang memukau.",
            "Kelompok ulasan ini menekankan apresiasi terhadap tata cahaya, pewarnaan adegan, dan kemegahan visual yang memperkuat atmosfer film.",
            "Topik ini mendiskusikan kualitas efek visual dan pengadeganan sinematik yang menjadi nilai tambah utama pada film ini."
        ]
    },
    "cerita": {
        "name": "Alur & Konstruksi Naskah",
        "label": "Struktur Alur & Narasi",
        "keywords": {
            # ── Unigram ──
            "plot", "story", "narrative", "ending", "script", "writing", "writer",
            "conclusion", "twist", "climax", "beginning", "pace", "pacing",
            "conflict", "chapter", "saga", "sequence", "half", "part", "original",
            "storyline", "subplot", "development", "arc",
            "opening", "finale", "resolution",
            "setup", "payoff", "structure", "theme", "themes", "message",
            # ── Bigram: Kritik Sosial & Tematis ──
            "social_commentary", "class_struggle", "metaphor_allegory", "dark_comedy",
            "poor_rich", "rich_poor", "difference_rich", "living_standard",
            "upper_class", "comedy_thriller", "crime_drama", "thriller_drama",
            "crime_horror", "thriller_horror", "foreign_language",
            # ── Bigram: Struktur Naratif ──
            "scientific_accuracy", "source_material", "tolkien_book", "read_book",
            "start_finish", "final_chapter", "high_school", "small_town",
            "japanese_culture", "mexican_culture", "installment_series",
            "perfect_conclusion", "palme_cannes", "south_korea",
        },
        "templates": [
            "Pembahasan ulasan ini terkonsentrasi pada struktur alur cerita, kerapian susunan naskah, serta penyelesaian adegan klimaks yang menjaga ketegangan alur.",
            "Kelompok ulasan ini menyoroti perkembangan narasi, kualitas kejutan alur (twist), dan konklusi babak akhir yang memuaskan ekspektasi audiens.",
            "Fokus ulasan audiens pada topik ini mengulas dinamika alur cerita dari awal hingga akhir serta cara sutradara mengemas konflik.",
            "Topik ini membahas tentang kekuatan naskah cerita dan konsistensi tempo penceritaan yang membuat penonton terus penasaran."
        ]
    },
    "musik": {
        "name": "Musik & Tata Suara",
        "label": "Musik & Tata Suara",
        "keywords": {
            # ── Unigram ──
            "score", "soundtrack", "music", "sound", "audio", "song", "songs",
            "musical", "theme", "composition", "radwimps", "zimmer", "melody",
            "track", "tracks", "composer", "orchestral", "background", "noise",
            "silence", "voice", "voices", "mixing",
            # ── Bigram ──
            "soundtrack_han", "notch_han", "fantastic_soundtrack", "sound_design",
            "music_choice", "randy_newman", "sound_effect",
        },
        "templates": [
            "Kelompok ulasan ini berfokus pada alunan musik pengiring (score), kualitas soundtrack, serta tata suara yang memperkuat emosi setiap adegan.",
            "Pembahasan audiens pada tema ini menyoroti keindahan aransement lagu dan tata audio yang berhasil membangun nuansa sinematik yang mendalam.",
            "Topik ini menekankan peran vital musik latar dalam menghidupkan suasana emosional cerita dan memberikan kesan membekas bagi penonton.",
            "Ulasan pada kelompok ini mengapresiasi komposisi musik pengiring yang padu dengan dinamika adegan di dalam film."
        ]
    },
    "emosi": {
        "name": "Kedalaman Emosi & Pesan Moral",
        "label": "Kesan Emosional & Pesan Moral",
        "keywords": {
            # ── Unigram ──
            "emotional", "moving", "touching", "powerful", "heart", "felt",
            "cry", "tear", "tears", "sad", "love", "family", "bond", "message",
            "meaningful", "soul", "feeling", "warm", "remember", "impact",
            "deeply", "touched", "inspired", "beautiful", "sentimental",
            "heartbreaking", "heartwarming", "empathy", "relate", "relatable",
            "hope", "joy", "grief", "loss", "journey", "life",
            # ── Bigram ──
            "emotional_rollercoaster", "emotional_weight", "father_daughter",
            "relationship_father", "emotional_philosophical", "important_message",
            "human_being", "life_death", "land_dead", "life_live",
            "never_fails", "start_finish",
        },
        "templates": [
            "Ulasan ini berpusat pada kedalaman emosi yang menyentuh perasaan penonton, pesan moral tentang keluarga, serta kehangatan nilai kehidupan.",
            "Kelompok ulasan ini menggambarkan kesan emosional audiens yang merasa terharu dan tersentuh oleh hubungan kasih sayang antar tokoh.",
            "Topik ini menyoroti daya dorong emosional cerita yang sukses membangkitkan rasa simpati dan keharuan mendalam bagi para penonton.",
            "Pembahasan audiens pada tema ini terkonsentrasi pada makna pesan moral yang disampaikan serta nuansa sentimental dalam cerita."
        ]
    },
    "aksi_scifi": {
        "name": "Aksi, Skala Epik & Sci-Fi",
        "label": "Aksi Epik & Dunia Sci-Fi",
        "keywords": {
            # ── Unigram ──
            "action", "battle", "war", "fight", "fighting", "epic", "universe",
            "space", "world", "earth", "heroic", "power", "sci-fi", "scifi",
            "monster", "infinity", "galaxy", "dimension", "gravity",
            "adventure", "quest", "mission", "chase", "explosion",
            "superhero", "weapon", "armor", "suit", "magic",
            "fantasy", "sword", "shield", "army", "soldier",
            # ── Bigram ──
            "science_fiction", "black_hole", "cinematic_universe", "final_battle",
            "theoretical_physicist", "human_race", "middle_earth", "mount_doom",
            "giant_spider", "space_ship", "waste_allocation", "space_odyssey",
            "space_ranger", "super_hero", "plant_life", "comic_book",
            "greatest_trilogy", "habitable_planet", "dust_storm",
        },
        "templates": [
            "Audiens banyak mendiskusikan adegan aksi yang memicu adrenalin, ketegangan pertempuran kolosal, serta megahnya skala dunia fiksi ilmiah.",
            "Kelompok ulasan ini berfokus pada serunya pertarungan epik, skala pertempuran yang megah, serta konsep fiksi ilmiah yang menantang imajinasi.",
            "Topik ini menyoroti intensitas adegan laga dan keberhasilan pembentukan alam semesta fiksi (world-building) yang fantastis.",
            "Pembahasan ulasan pada tema ini terkonsentrasi pada daya tarik adegan aksi berkecepatan tinggi dan nuansa petualangan yang epik."
        ]
    },
    "penilaian_umum": {
        "name": "Penilaian Umum & Kesan Penonton",
        "label": "Penilaian Umum Penonton",
        "keywords": {
            "amazing", "awesome", "incredible", "excellent", "perfect", "masterpiece",
            "brilliant", "outstanding", "superb", "fantastic", "wonderful",
            "terrible", "awful", "horrible", "disappointing", "disappointment",
            "boring", "overrated", "underrated", "mediocre", "average",
            "recommend", "recommended", "worth", "enjoyable", "entertaining",
            "enjoy", "enjoyed", "loved", "hated", "liked", "disliked",
            "opinion", "review", "overall", "definitely", "absolutely",
            "honestly", "personally", "classic", "must", "seen", "watched"
        },
        "templates": [
            "Kelompok ulasan ini mencerminkan kesan dan penilaian umum audiens terhadap film secara keseluruhan, mulai dari apresiasi hingga kritik menyeluruh.",
            "Topik ini merangkum sentimen umum penonton yang mengekspresikan kepuasan atau kekecewaan mereka terhadap kualitas film secara holistik.",
            "Ulasan pada kelompok ini didominasi oleh penilaian akhir penonton: apakah film layak ditonton, mengecewakan, atau melampaui ekspektasi.",
            "Pembahasan audiens pada tema ini mewakili kesan pertama dan kesimpulan umum setelah menyaksikan film dari awal hingga selesai."
        ]
    },
    "humor": {
        "name": "Humor & Komedi",
        "label": "Unsur Humor & Komedi",
        "keywords": {
            # ── Unigram ──
            "funny", "comedy", "humor", "humour", "laugh", "laughing", "laughed",
            "hilarious", "joke", "jokes", "wit", "witty", "silly", "absurd",
            "ridiculous", "amusing", "entertained", "fun", "lighthearted",
            "gag", "slapstick", "parody", "satire", "comic", "comedic",
            # ── Bigram ──
            "dark_comedy", "comedy_thriller", "romantic_comedy", "looney_tune",
        },
        "templates": [
            "Kelompok ulasan ini menyoroti unsur komedi dan humor dalam film yang berhasil menghibur penonton dengan tawa dan keceriaan.",
            "Topik ini mencerminkan apresiasi audiens terhadap gaya komedi, dialog lucu, dan momen-momen ringan yang menyegarkan suasana.",
            "Ulasan pada tema ini berfokus pada daya tarik humor film yang menjadi nilai jual utama dan sumber hiburan bagi penonton.",
            "Pembahasan ini terkonsentrasi pada kekuatan komedi situasional dan kepiawaian para pemain dalam menyampaikan momen humor."
        ]
    },
    "nostalgia": {
        "name": "Nostalgia & Kenangan Kolektif",
        "label": "Nilai Nostalgia & Kenangan",
        "keywords": {
            # ── Unigram ──
            "childhood", "nostalgia", "nostalgic", "classic", "remember",
            "memories", "memory", "decade", "remake", "reboot", "throwback",
            "grown", "grew", "youth", "generation", "era", "timeless",
            "iconic", "legend", "legendary", "franchise", "sequel", "prequel",
            "original", "return", "revive", "revival", "old", "retro",
            # ── Bigram ──
            "pizza_planet", "potato_head", "cowboy_doll",
            "book_life", "fairy_tale", "animation_industry",
        },
        "templates": [
            "Kelompok ulasan ini kaya akan nuansa nostalgia dan kenangan kolektif, di mana penonton mengaitkan film dengan ingatan masa kecil yang membekas.",
            "Topik ini mencerminkan ikatan emosional penonton dengan franchise atau karakter ikonik yang sudah menemani mereka lintas generasi.",
            "Ulasan pada tema ini didominasi sentimen nostalgis yang mengapresiasi nilai klasik film atau serial dan bagaimana ia relevan hingga kini.",
            "Pembahasan audiens ini menyuarakan kerinduan terhadap era atau gaya sinema tertentu yang dihidupkan kembali oleh film ini."
        ]
    }
}

# ==============================================================================
# 2. METODOLOGI DISTINCTIVENESS SCORE (METODE TF-IDF ANTAR-TOPIK)
# ==============================================================================
def calculate_topic_distinctiveness(
    topics_words_weights: List[List[Tuple[str, float]]], 
    top_n: int = 5
) -> List[List[str]]:
    """
    [METODOLOGI SKRIPSI]
    Menghitung skor kekhasan (distinctiveness) kata pada tiap topik terhadap topik lainnya.
    Formula:
      Distinctiveness(w, t) = Weight(w, t) / (Mean_Weight_Other_Topics(w) + 1e-6)
    
    Setelah dihitung, kata-kata dari LABEL_STOPWORDS dibuang sebelum dikembalikan.
    """
    K = len(topics_words_weights)
    if K == 1:
        # Hanya satu topik: filter stopword, kembalikan kata teratas
        result = [w for w, _ in topics_words_weights[0] if w not in LABEL_STOPWORDS]
        return [result[:top_n]]

    # Buat matriks bobot: word -> [weight_topic_0, weight_topic_1, ...]
    word_topic_matrix: Dict[str, List[float]] = {}
    for t_idx, topic in enumerate(topics_words_weights):
        for word, weight in topic:
            if word not in word_topic_matrix:
                word_topic_matrix[word] = [0.0] * K
            word_topic_matrix[word][t_idx] = float(weight)

    distinctive_keywords_per_topic: List[List[str]] = []

    for t_idx, topic in enumerate(topics_words_weights):
        scored_words: List[Tuple[str, float]] = []
        for word, weight in topic:
            # Hitung rata-rata bobot kata ini di topik LAIN
            other_weights = [
                word_topic_matrix[word][other_k]
                for other_k in range(K) if other_k != t_idx
            ]
            avg_other = sum(other_weights) / len(other_weights) if other_weights else 0.0
            distinctiveness_score = weight / (avg_other + 1e-6)
            scored_words.append((word, distinctiveness_score))

        # Urutkan berdasarkan skor kekhasan tertinggi
        scored_words.sort(key=lambda x: x[1], reverse=True)

        # Filter stopword sebelum dikembalikan
        filtered = [w for w, _ in scored_words if w not in LABEL_STOPWORDS]
        distinctive_keywords_per_topic.append(filtered[:top_n])

    return distinctive_keywords_per_topic


# ==============================================================================
# 3. OVERLAP SCORING KATEGORI TEMA & GENERASI TEMPLATE DINAMIS
# ==============================================================================
def classify_topic_category(
    topic_words: List[Tuple[str, float]]
) -> Tuple[str, str, str, float]:
    """
    [METODOLOGI SKRIPSI]
    Menentukan kategori tema dominan topik dengan menghitung Overlap Score terhadap
    Kamus Taksonomi Kategori Ulasan Film.
    
    Formula Overlap:
      OverlapScore(Category) = SUM_{i=0..N-1} (Weight(w_i) / (i + 1)) * IsInCategory(w_i)

    Pencocokan dilakukan secara berlapis:
      1. Cocokkan kata utuh (bigram/unigram) → bobot penuh.
      2. Cocokkan komponen kata dalam bigram (misal: 'science' dari 'science_fiction') → bobot setengah.
         Ini memastikan bigram baru yang belum masuk kamus tetap bisa cocok.
    
    Returns: (category_key, display_name, label, best_score)
    """
    category_scores: Dict[str, float] = {cat: 0.0 for cat in CATEGORY_TAXONOMY}

    for rank, (word, weight) in enumerate(topic_words):
        rank_weight = weight / (rank + 1.0)

        # Buat varian kata: kata utuh + setiap komponen jika bigram/trigram
        word_variants: Dict[str, float] = {word: 1.0}  # kata utuh → bobot penuh
        if '_' in word:
            parts = word.split('_')
            for part in parts:
                if part and part not in word_variants:
                    word_variants[part] = 0.5  # komponen → setengah bobot (fallback)

        for cat_key, cat_info in CATEGORY_TAXONOMY.items():
            for variant, variant_multiplier in word_variants.items():
                if variant in cat_info["keywords"]:
                    category_scores[cat_key] += rank_weight * variant_multiplier
                    break  # hanya hitung sekali per kata per kategori

    best_cat_key = max(category_scores, key=category_scores.get)
    best_score   = category_scores[best_cat_key]

    # Gunakan penilaian_umum hanya jika benar-benar tidak ada match sama sekali
    if best_score == 0.0:
        fallback = "penilaian_umum"
        return (
            fallback,
            CATEGORY_TAXONOMY[fallback]["name"],
            CATEGORY_TAXONOMY[fallback]["label"],
            0.0
        )

    return (
        best_cat_key,
        CATEGORY_TAXONOMY[best_cat_key]["name"],
        CATEGORY_TAXONOMY[best_cat_key]["label"],
        best_score
    )


# ==============================================================================
# 4. EKSTRAKSI CONTOH ULASAN REPRESENTATIF (REPRESENTATIVE REVIEWS)
# ==============================================================================
def extract_representative_reviews(
    topic_index: int,
    document_distributions: List[Dict[str, Any]],
    num_samples: int = 2,
    max_char_len: int = 220
) -> List[str]:
    """
    [METODOLOGI SKRIPSI]
    Mengambil potongan ulasan asli dari dataset yang memiliki skor kontribusi 
    probabilitas P(t | d) tertinggi untuk topik t.
    """
    topic_name = f"Topik {topic_index + 1}"

    matching_docs = [
        doc for doc in document_distributions
        if doc.get("dominant_topic") == topic_name
    ]
    matching_docs.sort(key=lambda x: x.get("probability", 0.0), reverse=True)

    representative_quotes: List[str] = []
    seen_texts = set()

    for doc in matching_docs:
        if len(representative_quotes) >= num_samples:
            break
        raw_text = str(doc.get("text", "")).strip()

        # Normalisasi whitespace dan karakter non-standar
        clean_text = re.sub(r'[\r\n\t]+', ' ', raw_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        # Deduplikasi: abaikan ulasan dengan isi yang sama
        snippet = clean_text[:60]
        if snippet in seen_texts:
            continue
        seen_texts.add(snippet)

        # Truncate pada batas kata (tidak memotong di tengah kata)
        if len(clean_text) > max_char_len:
            clean_text = clean_text[:max_char_len].rsplit(' ', 1)[0].rstrip('.,;:') + "..."

        if clean_text:
            representative_quotes.append(clean_text)

    # Fallback jika tidak ada dokumen dominan
    if not representative_quotes and document_distributions:
        for doc in document_distributions[:3]:
            raw = str(doc.get("text", "")).strip()
            clean = re.sub(r'\s+', ' ', raw)
            if clean:
                snippet = clean[:max_char_len].rsplit(' ', 1)[0].rstrip('.,;:') + "..."
                representative_quotes.append(snippet)
                break

    return representative_quotes


# ==============================================================================
# 5. MEMBANGUN KALIMAT INTERPRETASI YANG NATURAL
# ==============================================================================
def _build_interpretation_sentence(
    base_template: str,
    distinctive_words: List[str],
    cat_name: str
) -> str:
    """
    Membangun kalimat interpretasi final.
    Kata-kata khas yang ditemukan dijadikan frasa deskriptif yang natural,
    bukan sekadar deretan kata mentah teknis.
    """
    if not distinctive_words:
        return base_template

    # Jadikan kata-kata khas menjadi frasa yang lebih natural
    word_phrases = [f'"{w.replace("_", " ")}"' for w in distinctive_words[:3]]

    if len(word_phrases) == 1:
        evidence = f"Tema ini secara konsisten ditandai oleh kemunculan kata '{word_phrases[0]}' sebagai penanda topik yang membedakannya dari kelompok ulasan lain."
    elif len(word_phrases) == 2:
        evidence = (
            f"Topik ini secara konsisten ditandai oleh kemunculan kata "
            f"{word_phrases[0]} dan {word_phrases[1]} yang membedakannya dari kelompok ulasan lain."
        )
    else:
        evidence = (
            f"Topik ini secara konsisten ditandai oleh kemunculan kata "
            f"{', '.join(word_phrases[:-1])}, dan {word_phrases[-1]} "
            f"yang membedakannya dari kelompok ulasan lain."
        )

    return f"{base_template} {evidence}"


# ==============================================================================
# 6. ENGINE UTAMA INTERPRETASI TOPIK RULE-BASED
# ==============================================================================
def interpret_topic_rule_based(
    topic_index: int,
    topic_words_weights: List[Tuple[str, float]],
    all_topics_words_weights: List[List[Tuple[str, float]]],
    document_distributions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    [MAIN FUNCTION — v2]
    Menghasilkan struktur output interpretasi topik lengkap untuk frontend.

    Format Output:
    {
      "topic_id"      : "Topik 1",
      "label"         : "Penampilan Aktor & Karakter",
      "label_short"   : "Penampilan Aktor & Karakter",
      "kategori"      : "Akting & Penokohan Karakter",
      "interpretasi"  : "Pembahasan ulasan ini ...",
      "contoh_ulasan" : ["kutipan ulasan 1...", "kutipan ulasan 2..."],
      "top_words"     : [{"word": "actor", "weight": 0.035}, ...]
    }
    """
    topic_id = f"Topik {topic_index + 1}"

    # ── 1. Hitung Kata Khas (Distinctive Score)
    all_distinctive = calculate_topic_distinctiveness(all_topics_words_weights, top_n=5)
    distinctive_words = (
        all_distinctive[topic_index]
        if topic_index < len(all_distinctive)
        else [w for w, _ in topic_words_weights[:5] if w not in LABEL_STOPWORDS]
    )

    # ── 2. Klasifikasi Kategori Tema
    cat_key, cat_name, cat_label, cat_score = classify_topic_category(topic_words_weights)

    # ── 3. Label Topik (human-readable dari kategori, bukan kata mentah)
    #       Jika ada kata khas yang tidak ada di stopword, tampilkan 1–2 sebagai
    #       suplemen opsional. Namun label utama tetap dari nama kategori.
    label = cat_label  # Contoh: "Penampilan Aktor & Karakter"

    # ── 4. Pilih Template Kalimat (Round-Robin per Index Topik)
    templates = CATEGORY_TAXONOMY[cat_key]["templates"]
    template_idx = topic_index % len(templates)
    base_sentence = templates[template_idx]

    # ── 5. Bangun Kalimat Interpretasi yang Natural
    interpretasi_kalimat = _build_interpretation_sentence(
        base_sentence, distinctive_words, cat_name
    )

    # ── 6. Ambil Contoh Ulasan Representatif
    contoh_ulasan = extract_representative_reviews(
        topic_index, document_distributions, num_samples=2, max_char_len=220
    )

    # ── 7. Format Top Words
    top_words_formatted = [
        {"word": w, "weight": float(wt)}
        for w, wt in topic_words_weights[:10]
    ]

    return {
        "topic_id"     : topic_id,
        "label"        : label,
        "label_short"  : label,
        "kategori"     : cat_name,
        "interpretasi" : interpretasi_kalimat,
        "contoh_ulasan": contoh_ulasan,
        "top_words"    : top_words_formatted,
    }

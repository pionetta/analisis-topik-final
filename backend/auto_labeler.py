# -*- coding: utf-8 -*-
from typing import Any

# ==============================================================================
# KAMUS TEMA UTAMA & ATURAN LABEL DESKRIPTIF OTOMATIS
# ==============================================================================
TOPIC_THEMES = [
    {
        "label": "Visual & Animasi Sinematik",
        "keywords": {
            "animation", "animated", "pixar", "beautiful", "effect", "visual", 
            "art", "style", "graphic", "color", "cgi", "look", "scene", "screen",
            "frame", "shot", "lighting", "design", "beauty"
        },
        "description_template": "Ulasan pada kelompok topik ini berfokus pada keindahan tata visual, kualitas efek khusus, dan keanggunan gaya animasi yang memanjakan mata penonton."
    },
    {
        "label": "Akting & Penokohan Karakter",
        "keywords": {
            "character", "acting", "actor", "cast", "performance", "villain", 
            "hero", "role", "play", "joker", "batman", "woody", "buzz", "miles", 
            "mitsuha", "taki", "frodo", "gandalf", "thanos", "stark", "iron", "mcconaughey", "human"
        },
        "description_template": "Ulasan ini menyoroti pendalaman peran para aktor, kharisma penokohan karakter utama, serta daya tarik emosional tokoh di dalam cerita."
    },
    {
        "label": "Alur & Klimaks Cerita",
        "keywords": {
            "plot", "scene", "ending", "conclusion", "writer", "writing", 
            "script", "twist", "narrative", "saga", "story", "beginning", 
            "climax", "chapter", "pace", "pacing", "conflict", "half"
        },
        "description_template": "Pembahasan ulasan ini terkonsentrasi pada struktur alur cerita, penyusunan naskah, serta resolusi adegan klimaks yang menjaga ketegangan hingga penutup film."
    },
    {
        "label": "Aksi, Pertempuran & Dunia Sci-Fi",
        "keywords": {
            "action", "battle", "war", "fight", "epic", "universe", "space", 
            "world", "infinity", "earth", "heroic", "power", "sci-fi", "monster", "theatre"
        },
        "description_template": "Audiens banyak mendiskusikan adegan aksi yang memicu adrenalin, ketegangan pertempuran kolosal, serta megahnya pembangunan dunia fiksi ilmiah."
    },
    {
        "label": "Emosi, Pesan Moral & Musik",
        "keywords": {
            "love", "life", "family", "emotional", "heart", "felt", "music", 
            "score", "soundtrack", "cry", "tear", "sad", "touching", "message",
            "bond", "memorable", "soul", "feeling", "warm"
        },
        "focus": "kedalaman emosi dan kehangatan pesan moral",
        "description_template": "Ulasan ini berpusat pada kedalaman emosi yang menyentuh perasaan penonton, pesan moral tentang hubungan kekeluargaan, serta keindahan musik pengiring."
    }
]

def _humanize_words(words: list[str], limit: int = 3) -> str:
    selected = [w.replace("_", " ") for w in words[:limit]]
    if not selected:
        return "kata kunci utama"
    if len(selected) == 1:
        return f'"{selected[0]}"'
    return ", ".join(f'"{w}"' for w in selected[:-1]) + f' dan "{selected[-1]}"'

def interpret_topic(words: list[str]) -> dict[str, Any]:
    """
    Menghasilkan label deskriptif singkat dan kalimat interpretasi 
    yang spesifik, alami, dan bebas dari duplikasi teks.
    """
    word_set = set(words)
    
    best_theme = None
    max_score = -1.0
    
    for theme in TOPIC_THEMES:
        matches = word_set & theme["keywords"]
        if matches:
            score = sum(1.0 / (i + 1) for i, w in enumerate(words) if w in theme["keywords"]) + len(matches) * 0.25
            if score > max_score:
                max_score = score
                best_theme = theme
                
    evidence = _humanize_words(words)

    if not best_theme:
        # Generate dynamic label based on top 2 words if no theme matches
        top_2 = [w.capitalize() for w in words[:2]]
        label = " & ".join(top_2) if top_2 else "Topik Umum"
        notes = f"Ulasan pada kelompok ini membahas kombinasi topik umum seputar {evidence}."
    else:
        label = best_theme["label"]
        notes = f"{best_theme['description_template']} Hal ini diperkuat oleh dominasi kata kunci {evidence}."

    return {
        "label": label,
        "notes": notes
    }
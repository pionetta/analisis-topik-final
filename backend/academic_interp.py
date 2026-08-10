import sqlite3, json, re, requests

API_BASE = "http://127.0.0.1:5000"

# ================================================================
# FUNGSI INTERPRETASI AKADEMIK PER FILM
# Menghasilkan tuple (label, notes_terstruktur) berdasarkan
# kata dominan, contoh ulasan, dan pola semantik topik.
# ================================================================

def clean_label(text):
    """Pastikan label maks 5 kata."""
    words = text.split()
    return ' '.join(words[:5])

def build_notes(interpretasi, bukti, dominasi, ringkasan):
    """Bangun teks catatan berformat akademik."""
    return (
        f"**Interpretasi:** {interpretasi}\n\n"
        f"**Bukti:** {bukti}\n\n"
        f"**Dominasi Topik:** {dominasi}\n\n"
        f"**Ringkasan:** {ringkasan}"
    )

# ================================================================
# KAMUS ANALISIS PER FILM — FORMAT AKADEMIK LENGKAP
# ================================================================

# ── AVENGERS: ENDGAME ──────────────────────────────────────────

def analyze_avengers_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "russo_brother" in w and "emotional_rollercoaster" in w:
        return (
            "Penutup Epik Russo Brothers",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap arahan Russo Brothers dalam mengeksekusi penutup saga MCU yang dinilai sebagai perjalanan emosional yang berhasil. Ulasan dalam kelompok ini cenderung menyoroti ketepatan penceritaan yang mengikat 11 tahun narasi sinematik menjadi satu kesimpulan yang koheren dan memuaskan.",
                f"Kata dominan 'russo_brother' menunjukkan atribusi langsung terhadap sutradara; 'emotional_rollercoaster' dan 'perfect_conclusion' mengindikasikan respons afektif yang kuat. Contoh ulasan mendukung ini: \"{str(contoh[0])[:120]}...\" menggambarkan pengalaman emosional yang intens dari penonton.",
                f"Topik ini berkontribusi sekitar {dist_pct:.1f}% dari seluruh distribusi dokumen, menandakan bahwa apresiasi terhadap arahan dan penutup naratif merupakan salah satu tema yang cukup konsisten dibahas penonton.",
                "Penonton mengapresiasi arahan Russo Brothers yang berhasil menutup saga MCU dengan perjalanan emosional yang menguras perasaan."
            )
        )
    if "robert_downey" in w and "final_battle" not in w:
        return (
            "Pengorbanan Iron Man dan Kehilangan",
            build_notes(
                "Topik ini menangkap respons emosional penonton yang berpusat pada nasib Tony Stark sebagai karakter poros MCU. Diskusi dalam kelompok ini memperlihatkan dualitas antara rasa kehilangan yang mendalam atas kepergian karakter tersebut dan pertanyaan tentang keharusan naratif dari pengorbanan tersebut.",
                f"Kemunculan 'robert_downey' sebagai kata dengan bobot tertinggi menunjukkan sentralitas karakter Iron Man dalam diskusi ini. Kehadiran kata-kata negatif seperti 'not_give' dan 'not_be' mengindikasikan respons yang bernuansa — bukan sekadar pujian. Contoh ulasan: \"{str(contoh[0])[:120]}...\" memperlihatkan kompleksitas sentimen ini.",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mencerminkan seberapa besar proporsi diskusi yang terfokus pada dimensi personal dan karakter dibandingkan aspek aksi atau sinematik.",
                "Penonton terbagi antara haru atas pengorbanan Tony Stark dan pertanyaan tentang keharusan naratifnya."
            )
        )
    if "emotional_weight" in w or ("cinematic_universe" in w and "final_battle" in w):
        return (
            "Klimaks dan Bobot Emosional MCU",
            build_notes(
                "Topik ini merepresentasikan dimensi emosional dari pertempuran final Endgame dalam konteks yang lebih luas sebagai puncak dari seluruh Cinematic Universe Marvel. Kata-kata yang muncul mencerminkan beban naratif kumulatif yang dirasakan penonton setelah 22 film yang saling terhubung.",
                f"'Emotional_weight', 'cinematic_universe', dan 'final_battle' secara bersamaan mengindikasikan bahwa penonton tidak hanya menilai film ini secara mandiri, melainkan dalam konteks keseluruhan franchise. Ulasan seperti \"{str(contoh[0])[:120]}...\" memperkuat interpretasi ini.",
                f"Distribusi {dist_pct:.1f}% menunjukkan bahwa perspektif franchise-wide ini merupakan kerangka penilaian yang cukup umum digunakan penonton.",
                "Penonton menilai pertempuran final Endgame sebagai puncak emosional dari keseluruhan narasi MCU yang dibangun selama lebih dari satu dekade."
            )
        )
    if "perfect_conclusion" in w and "visual_effect" in w:
        return (
            "Visual Epik dan Kesempurnaan Penutup",
            build_notes(
                "Topik ini menangkap penilaian terpadu penonton terhadap dua dimensi utama Endgame: kualitas sinematik dari pertempuran dan keberhasilan film sebagai penutup yang memuaskan. Kedua aspek ini sering muncul bersamaan dalam ulasan yang memberikan nilai tinggi.",
                f"Kombinasi 'perfect_conclusion', 'final_battle', dan 'visual_effect' menunjukkan bahwa penonton memandang kehebatan visual dan kepuasan naratif sebagai dua hal yang saling menguatkan. Ulasan: \"{str(contoh[0])[:120]}...\" mencerminkan kepuasan menyeluruh ini.",
                f"Topik ini muncul pada {dist_pct:.1f}% distribusi, mengindikasikan proporsi penonton yang memberikan penilaian positif komprehensif.",
                "Penonton menilai Endgame sebagai penutup sempurna yang memadukan aksi visual epik dengan resolusi naratif yang memuaskan."
            )
        )
    # fallback: opini campuran/kritis
    return (
        "Ekspektasi Tidak Terpenuhi Sepenuhnya",
        build_notes(
            "Topik ini merepresentasikan suara penonton yang menilai Endgame dengan perspektif lebih kritis, di mana beberapa aspek film tidak sepenuhnya memenuhi ekspektasi yang tinggi. Dominasi kata-kata negasi mengindikasikan ulasan yang bernuansa atau mengandung ketidakpuasan.",
            f"Dominannya kata-kata negasi seperti 'not_give', 'not_as', 'not_be', dan 'not_the' mengindikasikan pola ulasan yang mengandung reservasi. Ini dapat mencerminkan kritik terhadap logika plot, pacing, atau penyelesaian karakter tertentu. Ulasan: \"{str(contoh[0])[:120]}...\"",
            f"Meski merupakan minoritas dengan {dist_pct:.1f}%, topik ini penting sebagai penyeimbang dalam analisis sentimen yang menyeluruh.",
            "Sebagian penonton menemukan bahwa Endgame tidak sepenuhnya memenuhi ekspektasi tinggi mereka pada aspek-aspek naratif tertentu."
        )
    )

def analyze_avengers_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "battle" in w and ("fan" in w or "saga" in w):
        return (
            "Antusiasme Fan dan Pertempuran Ikonik",
            build_notes(
                "Topik ini merepresentasikan ekspresi kolektif penggemar MCU dalam mengapresiasi pertempuran puncak dan narasi saga yang telah mereka ikuti. Ulasan dalam kelompok ini mencerminkan kebanggaan komunal sebagai bagian dari pengalaman franchise yang masif.",
                f"Kata 'battle', 'fan', 'saga', 'hero', dan 'universe' secara bersamaan membentuk semantik perayaan komunal. Ulasan: \"{str(contoh[0])[:120]}...\" memperlihatkan afeksi mendalam penonton terhadap perjalanan panjang ini.",
                f"Dengan distribusi {dist_pct:.1f}%, ini adalah perspektif yang cukup representatif dari basis penggemar yang luas.",
                "Penggemar MCU mengekspresikan kebanggaan dan antusiasme kolektif terhadap pertempuran epik sebagai kulminasi investasi emosional bertahun-tahun."
            )
        )
    if "conclusion" in w and ("perfect" in w or "wonderful" in w):
        return (
            "Penilaian Positif: Film Terbaik MCU",
            build_notes(
                "Topik ini merepresentasikan penilaian positif komprehensif dari penonton yang menilai Endgame sebagai pencapaian tertinggi franchise Marvel. Fokus pada kata-kata yang merujuk pada kesimpulan dan kesempurnaan menunjukkan kepuasan menyeluruh terhadap film.",
                f"'Conclusion', 'perfect', dan 'wonderful' membentuk cluster evaluasi positif yang konsisten. Frasa 'franchise' memperluas penilaian ke seluruh ekosistem MCU. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi ulasan yang memberikan penilaian terbaik secara keseluruhan.",
                "Penonton menilai Endgame sebagai penutup terbaik yang pernah ada dalam sejarah franchise superhero modern."
            )
        )
    if "not_give" in w or ("face" in w and "hulk" in w):
        return (
            "Kritik Naratif dan Ketidakpuasan Plot",
            build_notes(
                "Topik ini merepresentasikan dimensi kritis dari ulasan Endgame, di mana penonton mengidentifikasi kelemahan naratif spesifik. Kata-kata yang muncul merujuk pada karakter atau keputusan plot yang dianggap tidak konsisten atau mengecewakan.",
                f"'Not_give', 'face', 'hulk', 'fight', dan 'expectation' mengindikasikan kritik yang terfokus pada eksekusi karakter tertentu dan kesesuaian ekspektasi. Ulasan: \"{str(contoh[0])[:120]}...\" memberikan konteks kritik yang lebih spesifik.",
                f"Dengan distribusi {dist_pct:.1f}%, perspektif kritis ini mewakili proporsi penonton yang mengidentifikasi celah spesifik dalam narasi.",
                "Sebagian penonton mengidentifikasi kelemahan naratif dan inkonsistensi karakter yang mengurangi kepuasan menonton secara keseluruhan."
            )
        )
    if "nostalgia" in w or ("emotional" in w and "half" in w):
        return (
            "Nostalgia dan Haru Perjalanan MCU",
            build_notes(
                "Topik ini merepresentasikan dimensi sentimental Endgame sebagai film yang mengandalkan akumulasi afeksi penonton selama lebih dari satu dekade. Ulasan dalam kelompok ini cenderung menyoroti momen-momen yang secara sadar merujuk kembali pada film-film sebelumnya.",
                f"'Nostalgia', 'emotional', 'half', dan referensi karakter spesifik menunjukkan bahwa respons emosional ini bersifat intertekstual — terikat pada ingatan kolektif penonton sebagai penggemar MCU. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mencerminkan seberapa besar porsi pengalaman menonton Endgame yang diwarnai oleh memori terhadap film-film sebelumnya.",
                "Penonton merespons Endgame dengan nostalgia mendalam yang mengakumulasikan kenangan dari perjalanan 22 film MCU sebelumnya."
            )
        )
    return (
        "Narasi Saga dan Semesta Sinematik",
        build_notes(
            "Topik ini merepresentasikan penilaian penonton terhadap Endgame dalam kerangka yang lebih luas sebagai bagian dari proyek sinematik yang belum pernah ada sebelumnya. Diskusi cenderung memposisikan film bukan sebagai karya mandiri, melainkan sebagai simpul dari jaringan naratif yang kompleks.",
            f"Kata 'universe', 'saga', 'cinematic', dan 'original' membentuk kerangka penilaian berbasis franchise. Konteks ini memengaruhi cara penonton menginterpretasikan setiap keputusan naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Dengan distribusi {dist_pct:.1f}%, perspektif macro-franchise ini menunjukkan bahwa sebagian penonton mendekati film ini dengan kesadaran penuh akan ekosistemnya.",
            "Penonton menilai Endgame sebagai komponen dari proyek sinematik skala besar yang mendefinisikan ulang cara bercerita melalui medium film."
        )
    )

# ── COCO (2017) ────────────────────────────────────────────────

def analyze_coco_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "land_dead" in w and "animation_studio" in w and "mexican_culture" in w:
        return (
            "Dunia Orang Mati dan Visual Pixar",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap world-building Pixar dalam memvisualisasikan 'Land of the Dead' yang bersumber dari tradisi Dia de los Muertos. Ulasan dalam kelompok ini secara konsisten menyoroti cara Pixar mengubah konsep kematian menjadi dunia yang penuh warna dan kehidupan.",
                f"'Land_dead', 'mexican_culture', dan 'animation_studio' secara bersamaan menunjukkan koneksi antara representasi budaya dan pencapaian teknis animasi. Contoh ulasan: \"{str(contoh[0])[:120]}...\" memperlihatkan respons terhadap kekayaan visual ini.",
                f"Distribusi {dist_pct:.1f}% menunjukkan bahwa world-building dan representasi budaya merupakan aspek yang cukup menonjol dalam diskusi penonton.",
                "Penonton mengagumi cara Pixar memvisualisasikan dunia orang mati sebagai ruang yang penuh warna, detail budaya Meksiko, dan kehidupan yang paradoksal."
            )
        )
    if "heart_soul" in w or "kid_adult" in w:
        return (
            "Daya Pikat Lintas Generasi",
            build_notes(
                "Topik ini merepresentasikan kemampuan Coco untuk menjangkau penonton dari berbagai segmen usia secara bersamaan. Ulasan dalam kelompok ini menyoroti bagaimana film berhasil menyajikan lapisan makna berbeda — petualangan visual bagi anak-anak dan refleksi mendalam bagi orang dewasa.",
                f"'Heart_soul' dan 'kid_adult' secara eksplisit menunjukkan konsep universal appeal. Kehadiran 'beautiful_song' menambahkan dimensi musikal sebagai medium koneksi emosional. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini merefleksikan seberapa besar proporsi penonton yang secara aktif mengidentifikasi daya tarik lintas usia sebagai kekuatan utama film.",
                "Coco berhasil menyentuh hati penonton dari berbagai usia melalui lapisan makna yang berbeda namun sama-sama bermakna dalam satu narasi."
            )
        )
    if "fairy_tale" in w or "life_death" in w:
        return (
            "Tema Kematian sebagai Perayaan Kenangan",
            build_notes(
                "Topik ini merepresentasikan cara unik Coco dalam membahas kematian — bukan sebagai sesuatu yang menakutkan, melainkan sebagai bagian dari siklus ingatan dan perayaan. Ulasan dalam kelompok ini sering mengekspresikan kejutan positif atas pendekatan yang tidak lazim terhadap tema berat ini.",
                f"'Fairy_tale', 'life_death', 'no_longer', dan 'never_felt' menunjukkan perpaduan antara narasi dongeng dengan eksplorasi eksistensial tentang kematian dan kenangan. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang secara khusus mencatat pendekatan unik film terhadap tema kematian.",
                "Coco menghadirkan kematian sebagai perayaan kenangan melalui lensa dongeng yang hangat dan penuh kasih, bukan sebagai sesuatu yang perlu ditakuti."
            )
        )
    if "beautiful_animation" in w or "beautiful_song" in w:
        return (
            "Kualitas Animasi dan Musik Coco",
            build_notes(
                "Topik ini merepresentasikan penilaian teknis dan artistik terhadap kualitas produksi Coco. Ulasan dalam kelompok ini cenderung mengulas keindahan animasi dan kontribusi musik sebagai dua pilar utama pengalaman sinematik yang tak terlupakan.",
                f"'Beautiful_animation' dan 'beautiful_song' menunjukkan evaluasi estetis yang konsisten terhadap dua aspek produksi terkuat film ini. Kehadiran 'animation_studio' memperkuat atribusi terhadap pencapaian Pixar. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mencerminkan seberapa besar proporsi penonton yang mendekati film dari sudut pandang apresiasi teknis dan artistik.",
                "Penonton mengapresiasi Coco sebagai karya artistik yang memadukan keindahan animasi visual dengan kekuatan musik secara harmonis."
            )
        )
    return (
        "Tradisi Meksiko dan Perbandingan Tematik",
        build_notes(
            "Topik ini merepresentasikan diskusi penonton tentang dimensi budaya Coco, termasuk representasi tradisi Meksiko dan perbandingan dengan karya animasi sejenis. Ulasan dalam kelompok ini menunjukkan kesadaran penonton terhadap konteks budaya film.",
            f"'Book_life', 'mexican_tradition', dan 'mexican_culture' menunjukkan diskusi yang membandingkan Coco dengan The Book of Life atau mengulas keotentikan representasi budaya yang disajikan. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% mencerminkan proporsi penonton yang menempatkan film dalam konteks representasi budaya yang lebih luas.",
            "Penonton mendiskusikan Coco dalam konteks representasi budaya Meksiko dan kedudukannya di antara film-film animasi bertemakan Dia de los Muertos."
        )
    )

def analyze_coco_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "dead" in w and "land" in w and "not_a" not in w:
        return (
            "Dunia Arwah dan Kualitas Animasi",
            build_notes(
                "Topik ini merepresentasikan penilaian penonton terhadap representasi visual dunia arwah yang menjadi latar utama film, dikombinasikan dengan apresiasi terhadap kualitas animasi secara keseluruhan. Kedua aspek ini saling memperkuat dalam membentuk pengalaman sinematik yang unik.",
                f"'Dead', 'animation', 'land', dan 'emotional' mengindikasikan koneksi antara latar imajinatif dan respons emosional penonton. Ulasan: \"{str(contoh[0])[:120]}...\" memberikan bukti respons afektif terhadap elemen visual.",
                f"Distribusi {dist_pct:.1f}% menunjukkan bahwa kombinasi elemen visual dan emosional merupakan pola diskusi yang cukup sering muncul.",
                "Penonton mengapresiasi dunia arwah Coco sebagai latar yang visually stunning sekaligus menjadi medium penyampaian emosi yang kuat."
            )
        )
    if "beautiful" in w and "not_a" in w:
        return (
            "Penilaian Kritis dengan Pengakuan Estetis",
            build_notes(
                "Topik ini merepresentasikan ulasan yang mengakui keindahan Coco namun menyertakan catatan kritis. Pola ini mengindikasikan penonton yang memberikan penilaian bernuansa — tidak sepenuhnya memuji tanpa reservasi.",
                f"Perpaduan 'beautiful' (apresiasi estetis) dengan 'not_a' (negasi/pembatasan) dan 'song', 'tear' menunjukkan ulasan yang membedakan antara kekuatan film dan area yang dianggap kurang. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mewakili perspektif kritis yang tetap mengakui kekuatan artistik film.",
                "Penonton memberikan apresiasi terhadap keindahan Coco sambil menyertakan evaluasi kritis terhadap aspek-aspek naratif atau tematik tertentu."
            )
        )
    if "mexican" in w and ("culture" in w or "no_longer" in w):
        return (
            "Representasi Budaya Meksiko yang Autentik",
            build_notes(
                "Topik ini merepresentasikan diskusi penonton tentang keberhasilan Coco dalam merepresentasikan budaya Meksiko secara autentik dan penuh hormat. Ulasan dalam kelompok ini sering menyoroti detail tradisi yang jarang dikenal penonton internasional.",
                f"'Mexican', 'culture', 'no_longer', dan 'tradition' membentuk diskursus tentang identitas budaya dan representasi. 'Never_felt' menambahkan dimensi kebaruan pengalaman emosional yang terkait budaya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mengindikasikan bahwa representasi budaya adalah topik yang cukup signifikan dalam diskusi penonton.",
                "Penonton mengapresiasi representasi budaya Meksiko dalam Coco sebagai penggambaran yang autentik, penuh hormat, dan memperkenalkan tradisi yang kurang dikenal secara global."
            )
        )
    if ("kid" in w or "adult" in w) and ("tear" in w or "heart" in w):
        return (
            "Dampak Emosional yang Tak Terduga",
            build_notes(
                "Topik ini merepresentasikan respons emosional intens penonton — terutama momen-momen yang memicu tangis — yang sering kali digambarkan sebagai tidak terduga untuk sebuah film animasi. Penonton dari berbagai usia melaporkan pengalaman emosional serupa.",
                f"'Kid', 'adult', 'tear', 'heart', dan 'favorite' mengindikasikan dampak emosional yang lintas usia. Ketiadaan penghalang demografis memperkuat klaim tentang tema universal film. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, ini adalah salah satu topik yang paling mencerminkan kekuatan emosional utama Coco.",
                "Coco berhasil memicu respons emosional yang kuat dan tak terduga pada penonton dari berbagai usia, menjadikannya salah satu film animasi paling mengharukan yang pernah dibuat."
            )
        )
    if "muertos" in w or ("dream" in w and "tradition" in w):
        return (
            "Impian, Tradisi, dan Perayaan Budaya",
            build_notes(
                "Topik ini merepresentasikan tema musikal dan impian sebagai jantung naratif Coco, dikombinasikan dengan perayaan tradisi Dia de los Muertos. Hasrat Miguel terhadap musik menjadi kendaraan yang membawa pesan yang lebih dalam tentang identitas dan warisan.",
                f"'Muertos', 'tradition', 'dream', dan 'journey' membentuk narasi tentang impian personal dalam konteks warisan budaya. Kontras antara larangan keluarga dan passion musik memperkuat ketegangan naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar perhatian penonton terhadap tema impian dan identitas budaya sebagai inti cerita.",
                "Impian musikal Miguel dalam konteks tradisi Dia de los Muertos menjadi representasi tematik utama tentang identitas, warisan budaya, dan kebebasan berekspresi."
            )
        )
    if "song" in w and ("importance" in w or "musician" in w):
        return (
            "Musik sebagai Jembatan Antar Generasi",
            build_notes(
                "Topik ini merepresentasikan peran sentral musik — terutama lagu 'Remember Me' — sebagai elemen naratif yang melampaui fungsi hiburan. Ulasan dalam kelompok ini menyadari bahwa musik berfungsi sebagai metafora inti tentang ingatan dan koneksi antargenerasi.",
                f"'Song', 'importance', 'musician', dan 'value' menunjukkan bahwa penonton menilai musik bukan sekadar elemen estetis, melainkan komponen naratif yang fungsional dan bermakna. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mewakili penonton yang menganalisis musik sebagai bahasa naratif yang lebih dalam.",
                "Musik dalam Coco berfungsi sebagai jembatan naratif yang menghubungkan tema ingatan, hubungan antargenerasi, dan identitas budaya dalam satu medium yang universal."
            )
        )
    return (
        "Orisinalitas dan Kualitas Dunia Animasi",
        build_notes(
            "Topik ini merepresentasikan apresiasi terhadap orisinalitas konsep Coco dan kedetailan world-building yang dibangun Pixar. Ulasan dalam kelompok ini menyoroti keberanian studio dalam mengeksplorasi perspektif budaya yang jarang menjadi pusat narasi film animasi Hollywood.",
            f"'Animation', 'original', 'land', dan 'theme' menunjukkan evaluasi terhadap kebaruan dan kualitas pembangunan dunia fiksi. Ini berbeda dari topik yang berfokus pada emosi atau budaya secara khusus. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% mencerminkan proporsi penonton yang mendekati film dari perspektif orisinalitas dan inovasi naratif.",
            "Penonton mengapresiasi Coco sebagai karya orisinal yang membangun dunia fiksi dengan detail dan autentisitas yang melampaui standar film animasi konvensional."
        )
    )

# ── INTERSTELLAR (2014) ────────────────────────────────────────

def analyze_interstellar_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "scientific_accuracy" in w or "theoretical_physicist" in w:
        return (
            "Akurasi Saintifik dan Pengalaman Sinematik",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton yang menyoroti fondasi ilmiah Interstellar sebagai elemen yang membedakannya dari sains fiksi konvensional. Ulasan dalam kelompok ini sering merujuk pada kontribusi fisikawan Kip Thorne dan presisi visualisasi konsep-konsep fisika teoritis.",
                f"'Scientific_accuracy', 'theoretical_physicist', 'cinematic_experience', dan 'breathtaking_visuals' secara bersamaan mengindikasikan integrasi antara validitas ilmiah dan keunggulan sinematik. Contoh: \"{str(contoh[0])[:120]}...\" memperkuat karakteristik penonton yang teredukasi secara saintifik.",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa signifikan aspek akurasi ilmiah diperhatikan dalam diskusi penonton.",
                "Penonton mengapresiasi Interstellar sebagai karya sains fiksi yang langka karena mempertahankan presisi ilmiah sekaligus menghadirkan pengalaman sinematik yang mendalam."
            )
        )
    if "soundtrack_han" in w or "conclusion_credit" in w or "notch_han" in w:
        return (
            "Skor Hans Zimmer dan Evaluasi Akhir Film",
            build_notes(
                "Topik ini merepresentasikan diskusi penonton yang secara spesifik mengulas kontribusi skor musik Hans Zimmer dan penilaian terhadap akta penutup film. Kedua aspek ini sering muncul bersamaan dalam ulasan yang mengevaluasi Interstellar secara lebih kritis.",
                f"'Soundtrack_han', 'conclusion_credit', 'not_great', dan 'score_han' mengindikasikan ulasan yang memisahkan keberhasilan musik dari keberhasilan naratif. Ini menunjukkan penonton yang melakukan analisis komponen. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mewakili pandangan yang lebih analitis dan terfragmentasi terhadap elemen-elemen berbeda film.",
                "Penonton secara terpisah mengapresiasi skor musik Hans Zimmer sambil mendiskusikan kualitas akta penutup yang dinilai tidak sekuat bagian sebelumnya."
            )
        )
    if "attention_detail" in w and "dust_storm" in w:
        return (
            "Ketelitian Naratif dan Latar Bencana Lingkungan",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap cara Interstellar membangun urgensi keberangkatan melalui konteks lingkungan yang detail dan realistis. Latar bumi yang sekarat akibat badai debu berfungsi sebagai fondasi naratif yang memperkuat justifikasi misi luar angkasa.",
                f"'Attention_detail', 'dust_storm', 'stunning_visuals', dan 'human_race' menunjukkan apresiasi terhadap world-building yang tidak hanya estetis, tetapi juga fungsional secara naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menganalisis ketelitian naratif sebagai kekuatan khusus film ini.",
                "Penonton mengapresiasi ketelitian Interstellar dalam membangun konteks bencana lingkungan yang berfungsi sebagai fondasi naratif yang kuat dan meyakinkan."
            )
        )
    if "no_sense" in w or ("special_effect" in w and "no_words" in w):
        return (
            "Kritik Alur: Ambisi vs. Keterpahaman",
            build_notes(
                "Topik ini merepresentasikan pandangan kritis penonton yang merasa elemen-elemen ilmiah dan naratif Interstellar melampaui batas keterpahaman tanpa penjelasan yang memadai. Ulasan ini cenderung mengakui kecanggihan visual sambil mempertanyakan konsistensi logika cerita.",
                f"'No_sense', 'special_effect', 'no_words', dan 'no_idea' mengindikasikan pola kebingungan atau frustrasi naratif yang berbeda dari apresiasi. Kehadiran 'special_effect' menunjukkan pengakuan atas kualitas visual. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, perspektif kritis ini merepresentasikan suara penonton yang merasa ambisi ilmiah film melebihi kejelasan naratifnya.",
                "Sebagian penonton menemukan ketegangan antara ambisi ilmiah Interstellar yang tinggi dan kejelasan naratif yang mereka anggap tidak selalu proporsional."
            )
        )
    if "father_daughter" in w and "emotional_philosophical" in w:
        return (
            "Relasi Ayah-Anak sebagai Inti Emosional",
            build_notes(
                "Topik ini merepresentasikan dimensi emosional terdalam Interstellar — hubungan Cooper-Murph yang menjadi jangkar emosional di tengah kompleksitas konsep fisika. Penonton yang masuk dalam kelompok ini mengidentifikasi lapisan personal ini sebagai elemen yang paling berkesan.",
                f"'Father_daughter', 'relationship_father', 'emotional_philosophical', dan 'church_organ' bersama menciptakan cluster emosional-filosofis. Organ sebagai instrumen menambahkan dimensi spiritual. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan bahwa hubungan interpersonal sebagai jangkar emosional adalah aspek yang cukup diperhatikan penonton.",
                "Hubungan ayah-anak antara Cooper dan Murph berfungsi sebagai inti emosional yang memberikan dimensi personal di tengah narasi saintifik yang kompleks."
            )
        )
    if "black_hole" in w and "visual_effect" in w and "anne_hathaway" in w:
        return (
            "Visualisasi Lubang Hitam dan Ensemble Cast",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap dua aspek: visualisasi lubang hitam yang belum pernah terlihat sebelumnya di layar lebar, dan penampilan ensemble cast. Kedua elemen ini sering disebutkan bersamaan dalam ulasan yang menilai film dari sudut pandang sinematik.",
                f"'Black_hole', 'visual_effect', 'anne_hathaway', dan 'matthew_mcconaughey' menunjukkan koneksi antara pencapaian visual dengan performa aktor. Kontribusi Kip Thorne dalam visualisasi Gargantua sering menjadi rujukan. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini merefleksikan penonton yang menggabungkan apresiasi teknis dan apresiasi akting.",
                "Penonton mengapresiasi visualisasi lubang hitam Gargantua sebagai terobosan sinematik yang dipadukan dengan performa akting ensemble yang meyakinkan."
            )
        )
    if "attention_detail" in w or "dark_knight" in w:
        return (
            "Warisan Nolan dan Standar Sains Fiksi",
            build_notes(
                "Topik ini merepresentasikan penilaian Interstellar dalam konteks filmografi Christopher Nolan secara keseluruhan. Penonton membandingkan film ini dengan karya-karya sebelumnya dan mengevaluasinya sebagai kontribusi terhadap genre sains fiksi.",
                f"'Dark_knight' sebagai referensi komparatif, 'attention_detail', 'science_fiction', dan 'han_score' menunjukkan evaluasi berbasis perbandingan karya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mendekati film dengan kerangka komparatif terhadap filmografi Nolan.",
                "Penonton menempatkan Interstellar dalam konteks warisan sinematik Christopher Nolan dan kontribusinya terhadap redefinisi standar genre sains fiksi kontemporer."
            )
        )
    if "human_race" in w and "matthew_mcconaughey" in w:
        return (
            "Misi Kemanusiaan dan Performa McConaughey",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap tema misi penyelamatan umat manusia dan performa Matthew McConaughey sebagai Cooper. Ulasan dalam kelompok ini cenderung menyoroti bagaimana McConaughey berhasil membumikan narasi kosmis melalui interpretasi yang penuh kemanusiaan.",
                f"'Human_race' mengindikasikan kesadaran penonton terhadap skala naratif film; 'matthew_mcconaughey' menunjukkan atribusi terhadap performa individual. 'Search_habitable' memperkuat fokus pada misi itu sendiri. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mewakili penonton yang melihat film melalui lensa karakter dan misi utamanya.",
                "Penonton menilai performa Matthew McConaughey sebagai elemen yang berhasil membumikan narasi tentang kelangsungan umat manusia menjadi pengalaman yang personal dan emosional."
            )
        )
    return (
        "Ambisi Saintifik Sains Fiksi Nolan",
        build_notes(
            "Topik ini merepresentasikan penilaian umum penonton terhadap Interstellar sebagai karya sains fiksi yang ambisius dari Christopher Nolan. Ulasan dalam kelompok ini mengidentifikasi film ini sebagai sebuah upaya untuk mendorong batas genre.",
            f"Kombinasi kata-kata seperti 'science_fiction', 'matthew_mcconaughey', dan 'visual_effect' membentuk gambaran umum tentang film. Contoh: \"{str(contoh[0])[:120]}...\" memberikan konteks tambahan.",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi ulasan yang memberikan penilaian umum tanpa fokus pada aspek spesifik tertentu.",
            "Penonton menilai Interstellar sebagai ambisi saintifik Christopher Nolan yang mengeksplorasi batas fisika dan emosi manusia secara bersamaan."
        )
    )

def analyze_interstellar_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "imax" in w or ("visuals" in w and "gravity" in w):
        return (
            "Pengalaman IMAX dan Visual Luar Angkasa",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap dimensi sinematik Interstellar sebagai film yang dirancang untuk pengalaman IMAX. Ulasan mengidentifikasi penggunaan kamera IMAX dan pemilihan lokasi nyata sebagai faktor yang mengangkat imersivitas.",
                f"'Imax', 'visuals', 'gravity', 'effect', dan 'humanity' mengindikasikan bahwa penonton menilai pengalaman menonton sebagai komponen integral penilaian. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan bahwa aspek sinematografi dan pengalaman bioskop adalah pertimbangan yang cukup signifikan.",
                "Penonton mengidentifikasi pengalaman IMAX dan kualitas sinematografi luar angkasa sebagai dua faktor pembentuk pengalaman menonton yang tak terlupakan."
            )
        )
    if "science" in w and "emotional" in w and "christopher" in w:
        return (
            "Sintesis Sains, Emosi, dan Visi Nolan",
            build_notes(
                "Topik ini merepresentasikan penilaian integratif terhadap keberhasilan Nolan menyatukan akurasi saintifik dengan kedalaman emosional. Penonton dalam kelompok ini mengidentifikasi kemampuan ini sebagai pencapaian paling signifikan film.",
                f"'Science', 'emotional', 'christopher', dan 'scientific' membentuk penilaian yang tidak memisahkan antara aspek intelektual dan afektif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, ini merupakan pola penilaian yang mengintegrasikan multiple dimensi secara bersamaan.",
                "Penonton mengidentifikasi kemampuan Nolan menyintesiskan akurasi saintifik dengan kedalaman emosional sebagai pencapaian paling signifikan Interstellar."
            )
        )
    if "no_sense" in w and ("emotional" in w or "inception" in w):
        return (
            "Akhir Cerita yang Memecah Opini",
            build_notes(
                "Topik ini merepresentasikan polarisasi penonton terhadap akta ketiga Interstellar. Sebagian penonton menganggap ending sebagai resolusi jenius berbasis sains, sementara yang lain merasa logika naratif menjadi terlalu abstrak untuk dipahami secara memuaskan.",
                f"'No_sense', 'emotional', 'inception', dan 'christopher' menunjukkan penonton yang membandingkan ambiguitas Interstellar dengan film Nolan lainnya. Referensi ke Inception mengindikasikan ekspektasi tentang cara Nolan menyelesaikan kompleksitas naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa signifikan perdebatan tentang akta ketiga dalam keseluruhan diskusi.",
                "Akta ketiga Interstellar memecah opini penonton antara mereka yang menganggapnya sebagai resolusi jenius dan yang merasa narasi menjadi terlalu abstrak."
            )
        )
    if "music" in w and ("credit" in w or "emotion" in w):
        return (
            "Skor Musik dan Dampak Emosional Menyeluruh",
            build_notes(
                "Topik ini merepresentasikan pengakuan penonton terhadap kontribusi krusial skor musik Hans Zimmer dalam membentuk pengalaman emosional Interstellar. Musik diidentifikasi bukan hanya sebagai pelengkap visual, tetapi sebagai komponen naratif yang berdiri sendiri.",
                f"'Music', 'emotion', 'credit', dan 'visuals' menunjukkan bahwa penonton mengaitkan dampak emosional secara langsung dengan pilihan musikal. Skor organ Hans Zimmer sering disebutkan. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini merefleksikan seberapa besar peran musik dalam membentuk respons afektif penonton.",
                "Skor musik Hans Zimmer diidentifikasi penonton sebagai komponen naratif mandiri yang secara langsung membentuk intensitas emosional Interstellar."
            )
        )
    if "science" in w and "planet" in w and "fiction" in w:
        return (
            "Debat Akurasi Ilmiah dalam Sains Fiksi",
            build_notes(
                "Topik ini merepresentasikan diskusi penonton yang mengevaluasi Interstellar dari perspektif akurasi ilmiah. Kelompok ini cenderung memiliki latar belakang atau minat pada sains, sehingga penilaian mereka lebih spesifik tentang di mana film mempertahankan kebenaran ilmiah dan di mana mengambil kebebasan naratif.",
                f"'Science', 'planet', 'fiction', 'mcconaughey', dan 'earth' menunjukkan penonton yang mengevaluasi konsistensi ilmiah dalam konteks narasi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mendekati film dengan kerangka evaluasi berbasis pengetahuan saintifik.",
                "Penonton dengan literasi saintifik mendiskusikan Interstellar dalam kerangka evaluasi akurasi ilmiah dan kebebasan naratif yang diambil sutradara."
            )
        )
    if "no_idea" in w or "no_words" in w or "never_fails" in w:
        return (
            "Kekaguman Tak Tertahankan dan Speechlessness",
            build_notes(
                "Topik ini merepresentasikan respons penonton yang mengalami kesulitan dalam mengekspresikan kekaguman mereka terhadap Interstellar melalui kata-kata biasa. Kondisi 'speechless' ini menjadi salah satu indikator dampak sinematik yang paling kuat.",
                f"'No_idea', 'no_words', 'never_fails', 'excellent', dan 'visuals' menunjukkan pola ulasan yang menyatakan keterbatasan bahasa dalam mendeskripsikan pengalaman menonton. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mewakili ekstrem positif dari spektrum respons afektif penonton.",
                "Sebagian penonton melaporkan pengalaman menonton yang melampaui kemampuan deskripsi verbal, menunjukkan dampak sinematik Interstellar yang paling intens."
            )
        )
    if "earth" in w and ("theory" in w or "han" in w):
        return (
            "Teori Relativitas dan Dilema Keterpisahan",
            build_notes(
                "Topik ini merepresentasikan momen emosional paling berkesan dalam Interstellar — ketika penonton memahami implikasi dilatasi waktu dan apa artinya bagi hubungan antarkarakter. Momen ini sering digambarkan sebagai yang paling menghancurkan secara emosional.",
                f"'Earth', 'theory', 'music', 'mcconaughey', dan 'han' mengindikasikan koneksi antara konsep fisika (relativitas waktu) dengan dampak emosionalnya pada karakter dan penonton. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang merespons secara khusus terhadap konsekuensi emosional dari premis fisika film.",
                "Konsep dilatasi waktu yang divisualisasikan Interstellar membangkitkan respons emosional paling mendalam ketika penonton merasakan implikasinya bagi hubungan antar karakter."
            )
        )
    if "human" in w and ("planet" in w or "able" in w):
        return (
            "Misi Kemanusiaan dan Kemampuan Manusia",
            build_notes(
                "Topik ini merepresentasikan diskusi penonton tentang tema inti Interstellar — kemampuan dan keterbatasan manusia dalam menghadapi ancaman eksistensial. Ulasan dalam kelompok ini mengeksplorasi pertanyaan tentang batas-batas pencapaian ilmu pengetahuan dan keberanian manusia.",
                f"'Human', 'planet', 'not_know', dan 'able' menunjukkan diskursus tentang potensi dan keterbatasan. Konteks misi pencarian planet layak huni memperkuat tema survival. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mewakili penonton yang mendekati film dari perspektif tematis tentang eksistensi manusia.",
                "Interstellar mendorong penonton untuk merenungkan kemampuan dan keterbatasan manusia dalam menghadapi krisis eksistensial yang memerlukan pengorbanan ekstrem."
            )
        )
    return (
        "Penilaian Umum Film Sains Fiksi",
        build_notes(
            "Topik ini merepresentasikan penilaian umum penonton terhadap Interstellar sebagai film sains fiksi tanpa fokus pada aspek spesifik tertentu. Ulasan dalam kelompok ini memberikan evaluasi holistik yang mencakup berbagai dimensi.",
            f"Kombinasi kata-kata yang beragam tanpa satu tema dominan yang kuat mengindikasikan penilaian komprehensif. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi ulasan dengan perspektif menyeluruh.",
            "Penonton memberikan penilaian komprehensif terhadap Interstellar sebagai film sains fiksi yang mengintegrasikan berbagai dimensi sinematik dan naratif."
        )
    )

# ── PARASITE (2019) ────────────────────────────────────────────

def analyze_parasite_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "metaphor_allegory" in w and ("poor_rich" in w or "difference_rich" in w):
        return (
            "Alegori Kelas Sosial dan Ketimpangan",
            build_notes(
                "Topik ini merepresentasikan pemahaman penonton terhadap Parasite sebagai alegori sistemik tentang ketimpangan ekonomi. Ulasan dalam kelompok ini mengidentifikasi lapisan simbolik film — dari ruang fisik hingga dialog — sebagai representasi hierarki sosial yang disengaja dan terencana.",
                f"'Metaphor_allegory', 'difference_rich', 'poor_rich', dan 'social_commentary' membentuk diskursus kritis tentang representasi kelas sosial. Ini menunjukkan penonton yang mampu membaca film di luar permukaan naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mengindikasikan seberapa besar proporsi penonton yang menganalisis film pada level tematik dan alegoris.",
                "Penonton mengidentifikasi Parasite sebagai alegori yang cermat tentang ketimpangan kelas sosial, di mana setiap detail naratif dan sinematik berfungsi sebagai representasi simbolis."
            )
        )
    if "foreign_language" in w and ("edge_seat" in w or "thriller_drama" in w):
        return (
            "Ketegangan Thriller Melampaui Hambatan Bahasa",
            build_notes(
                "Topik ini merepresentasikan respons penonton yang mengalami bahwa kualitas naratif Parasite berhasil mengatasi hambatan bahasa dan mempertahankan ketegangan sepanjang film. Ini merupakan pencapaian signifikan untuk film non-Inggris.",
                f"'Foreign_language', 'edge_seat', 'thriller_drama', dan 'without_any' menunjukkan pengakuan eksplisit terhadap hambatan bahasa yang berhasil diatasi oleh kekuatan narasi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini merepresentasikan penonton internasional yang secara khusus mencatat pengalaman menonton film subtitel.",
                "Kualitas narasi Parasite terbukti mampu mempertahankan ketegangan thriller secara efektif bahkan bagi penonton yang biasanya enggan menonton film berbahasa asing."
            )
        )
    if "south_korea" in w and ("palme_cannes" in w or "living_standard"):
        return (
            "Konteks Korea dan Pengakuan Global",
            build_notes(
                "Topik ini merepresentasikan diskusi penonton tentang konteks sosial-ekonomi Korea yang spesifik dan signifikansi global Parasite melalui penghargaan internasional. Ulasan ini sering menempatkan film dalam konteks industri film global.",
                f"'South_korea', 'palme_cannes', 'living_standard', dan 'class_struggle' menunjukkan diskursus yang melampaui teks film menuju konteks produksi dan receptionnya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mendekati film dengan konteks industri dan sosial yang lebih luas.",
                "Penonton mendiskusikan Parasite dalam konteks kondisi sosial-ekonomi Korea Selatan yang spesifik dan dampaknya terhadap pengakuan dan penerimaan global film ini."
            )
        )
    if "dark_comedy" in w and ("comedy_thriller" in w or "class_struggle" in w):
        return (
            "Hibriditas Genre: Komedi Gelap dan Thriller",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap kemampuan Bong Joon-ho memadukan genre yang secara konvensional tidak kompatibel. Perpaduan komedi, thriller, dan drama sosial dalam satu film dinilai sebagai pencapaian tonalitas yang langka.",
                f"'Dark_comedy', 'comedy_thriller', 'class_struggle', dan 'social_commentary' menunjukkan kesadaran penonton terhadap permainan genre yang disengaja. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan seberapa besar proporsi penonton yang mengidentifikasi hibriditas genre sebagai daya tarik utama.",
                "Penonton mengapresiasi kemampuan Bong Joon-ho dalam mengintegrasikan komedi gelap, thriller, dan satir sosial menjadi satu tonalitas naratif yang koheren."
            )
        )
    if "upper_class" in w and ("thriller_horror" in w or "social_commentary" in w):
        return (
            "Teror Kelas Atas dan Elemen Horror",
            build_notes(
                "Topik ini merepresentasikan respons penonton terhadap perubahan nada dramatis Parasite dari satir komedi menjadi thriller yang mengandung elemen horror. Transformasi ini diidentifikasi sebagai titik balik naratif yang paling mengejutkan.",
                f"'Upper_class', 'social_commentary', 'thriller_horror', dan 'edge_seat' menunjukkan respons terhadap eskalasi ketegangan dan perubahan genre yang mendadak. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar perhatian penonton terhadap elemen horror dan thriller dalam struktur naratif film.",
                "Pergeseran tonal Parasite dari komedi satir menuju thriller berdarah diidentifikasi penonton sebagai momen naratif yang paling mengejutkan dan efektif."
            )
        )
    return (
        "Ambiguitas Moral Kaya-Miskin",
        build_notes(
            "Topik ini merepresentasikan respons penonton terhadap posisi moral yang ambigu dalam Parasite — film yang tidak secara eksplisit memihak kelas sosial manapun. Penonton yang masuk dalam kelompok ini merasakan ketidaknyamanan produktif dalam menentukan simpati mereka.",
            f"'Rich_poor', 'not_a', 'dark_comedy', dan 'not_be' mengindikasikan kerangka penilaian yang bernuansa tanpa simpati tunggal. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% mencerminkan seberapa besar proporsi penonton yang mencatat ambiguitas moral sebagai kekuatan naratif film.",
            "Parasite sengaja menempatkan penonton dalam posisi simpati yang terus berganti, menciptakan ketidaknyamanan moral yang menjadi instrumen kritik sosial yang efektif."
        )
    )

def analyze_parasite_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "thriller" in w and ("twist" in w or "cast" in w):
        return (
            "Twist Plot dan Ketegangan Thriller",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap struktur naratif Parasite yang menggunakan plot twist secara efektif untuk mempertahankan ketegangan. Ulasan mengidentifikasi momen-momen perubahan naratif sebagai titik paling berkesan.",
                f"'Thriller', 'twist', 'cast', dan 'class' menunjukkan kombinasi antara elemen genre dan kekaguman terhadap performa ensemble. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi elemen thriller dan twist sebagai daya tarik utama.",
                "Penonton mengapresiasi efektivitas plot twist Parasite sebagai mekanisme naratif yang berhasil mempertahankan ketegangan dan membalik ekspektasi secara konsisten."
            )
        )
    if "life" in w and ("child" in w or "young" in w) and "class" in w:
        return (
            "Kehidupan Sehari-hari dan Realitas Sosial Korea",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap detail kehidupan sehari-hari yang dihadirkan Parasite sebagai konteks yang memvalidasi konflik kelas sosialnya. Ulasan mengidentifikasi keautentikan detail ini sebagai fondasi yang membuat ketegangan naratif terasa nyata.",
                f"'Life', 'child', 'social', 'korea', dan 'class' menunjukkan fokus pada dimensi sosiologis kehidupan keluarga miskin di Korea kontemporer. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menilai keautentikan detail kehidupan sebagai kekuatan naratif.",
                "Keautentikan detail kehidupan sehari-hari keluarga miskin Korea Selatan menjadi fondasi yang membuat konflik kelas Parasite terasa nyata dan relevan."
            )
        )
    if "drama" in w and ("horror" in w or "dark" in w) and "comedy" in w:
        return (
            "Drama Gelap dan Transisi Genre yang Mengejutkan",
            build_notes(
                "Topik ini merepresentasikan respons penonton terhadap perubahan tonalitas film yang terjadi di paruh kedua Parasite. Transisi dari komedi satir menuju drama gelap dengan elemen horror diidentifikasi sebagai keputusan naratif yang berani dan efektif.",
                f"'Drama', 'dark', 'comedy', 'thriller', dan 'horror' menunjukkan kesadaran terhadap multiplanaritas genre. Kontras antara komedi dan horror memperkuat kejutan naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mencerminkan perhatian penonton terhadap keunikan tonalitas yang menjadi ciri khas Bong Joon-ho.",
                "Transisi dramatik dari komedi satir menuju drama gelap berdarah diidentifikasi sebagai keputusan tonalitas Bong Joon-ho yang paling berani dan mengejutkan."
            )
        )
    if ("not_a" in w or "worth" in w) and ("rich" in w or "poor" in w):
        return (
            "Evaluasi Kritis terhadap Nilai Film",
            build_notes(
                "Topik ini merepresentasikan diskusi penonton yang mengevaluasi Parasite secara lebih terukur — mempertimbangkan apakah film benar-benar layak mendapat reputasinya. Ulasan dalam kelompok ini cenderung lebih analitis dan tidak sepenuhnya terbawa sentimen positif massal.",
                f"'Not_a', 'worth', 'rich', 'poor', dan 'aspect' menunjukkan pendekatan evaluatif yang mencari keseimbangan antara pujian dan kritik. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang memberikan penilaian lebih terkalibrasi.",
                "Sebagian penonton mengevaluasi Parasite secara lebih kritis dengan mempertimbangkan apakah kualitas film secara keseluruhan sepadan dengan reputasinya yang luar biasa."
            )
        )
    if "oscar" in w or "foreign" in w:
        return (
            "Oscar dan Implikasi bagi Sinema Global",
            build_notes(
                "Topik ini merepresentasikan diskusi tentang kemenangan Oscar Parasite dan implikasinya terhadap pengakuan sinema non-Anglofon secara global. Ulasan ini sering bersifat meta — mendiskusikan film dalam konteks industri dan kebijakan penghargaan.",
                f"'Oscar', 'foreign', 'fact', dan 'rich' menunjukkan diskursus tentang industri dan pengakuan institusional. Kemenangan Oscar sebagai titik referensi mengangkat pertanyaan tentang definisi 'film terbaik'. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mencerminkan penonton yang menempatkan film dalam konteks meta-industri film global.",
                "Kemenangan Oscar Parasite memancing diskusi lebih luas tentang kesetaraan pengakuan sinema internasional dan bias historis industri penghargaan film."
            )
        )
    if "cinematography" in w or "complex" in w:
        return (
            "Sinematografi dan Kompleksitas Naratif",
            build_notes(
                "Topik ini merepresentasikan apresiasi teknis terhadap aspek sinematografi dan kompleksitas naratif Parasite yang sering terabaikan di balik diskusi tematik yang lebih dominan. Penonton dalam kelompok ini mengidentifikasi keputusan sinematik sebagai komponen penting.",
                f"'Cinematography', 'complex', 'single', dan 'message' menunjukkan analisis teknis terhadap komposisi dan struktur naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mewakili sudut pandang sinefil yang mengevaluasi film dari perspektif teknis.",
                "Penonton yang teredukasi secara sinematik mengidentifikasi sinematografi Hong Kyung-pyo dan kompleksitas naratif Bong Joon-ho sebagai keunggulan teknis yang menopang kekuatan tematik film."
            )
        )
    if "jung" in w or "park" in w or "funny" in w:
        return (
            "Karakter Ki-taek dan Komedi yang Menguras Energi",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap aspek komedi dan karisma karakter keluarga Ki-taek dalam Parasite. Humor yang lahir dari situasi dan karakter diidentifikasi sebagai komponen yang membuat kritik sosial film tersampaikan tanpa terasa didaktis.",
                f"'Jung', 'park', 'funny', 'life', dan 'society' menunjukkan fokus pada dimensi komedi dan dinamika karakter. Konteks sosial memperkuat fungsi humor sebagai instrument satir. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi komedi situasional sebagai kekuatan naratif yang signifikan.",
                "Humor situasional yang lahir dari karakter keluarga Ki-taek berfungsi sebagai instrumen satir yang efektif dalam menyampaikan kritik kelas sosial tanpa nada yang eksplisit didaktis."
            )
        )
    return (
        "Komedi Satir dan Kritik Kelas Sosial",
        build_notes(
            "Topik ini merepresentasikan penilaian integratif penonton yang mengidentifikasi komedi satir sebagai wahana utama kritik sosial dalam Parasite. Hubungan antara tawa dan ketidaknyamanan moral dianggap sebagai formula naratif yang paling khas dari Bong Joon-ho.",
            f"'Comedy', 'social', 'dark', 'thriller', dan 'horror' membentuk jaringan semantik tentang penggunaan humor sebagai kritik. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menilai film melalui lensa komedi satir sebagai bahasa utama.",
            "Parasite menggunakan komedi satir sebagai bahasa utama kritik sosial, menciptakan pengalaman di mana tawa dan ketidaknyamanan moral hadir secara bersamaan dan tidak terpisahkan."
        )
    )

# ── SPIDER-VERSE (2018) ────────────────────────────────────────

def analyze_spiderverse_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "jake_johnson" in w and ("never_seen" in w or "not_for" in w):
        return (
            "Karakter Baru dan Pengalaman yang Belum Pernah Ada",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap hadirnya karakter-karakter baru — terutama versi Peter Parker yang lebih tua — sebagai pendamping Miles Morales yang memberikan dimensi emosional berbeda. Pengalaman menonton yang unik menjadi tema sentral.",
                f"'Jake_johnson', 'never_seen', 'comic_book', dan 'not_for' menunjukkan kejutan positif terhadap pengelolaan karakter yang tidak konvensional. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang secara khusus mencatat kebaruan pengalaman dan karakter sebagai nilai utama.",
                "Hadirnya Peter Parker yang lebih tua dan karakter-karakter Spider-Man baru memberikan pengalaman sinematik yang benar-benar belum pernah ada sebelumnya dalam genre superhero."
            )
        )
    if "animation_style" in w and ("gwen_stacy" in w or "super_hero" in w) and "post_credit" not in w:
        return (
            "Gaya Animasi Revolusioner dan Karakter Perempuan",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap gaya animasi yang secara radikla berbeda dari konvensi CGI dan hadirnya Gwen Stacy sebagai karakter perempuan yang kuat. Keduanya dipandang sebagai inovasi yang saling memperkuat.",
                f"'Animation_style', 'gwen_stacy', 'comic_book', dan 'super_hero' mengindikasikan koneksi antara pencapaian artistik dan representasi karakter. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi inovasi visual dan representasi karakter sebagai nilai utama.",
                "Gaya animasi yang mereplikasi estetika komik cetak dikombinasikan dengan hadirnya karakter perempuan yang kuat menjadi pencapaian ganda yang mendefinisikan Spider-Verse."
            )
        )
    if "animation_style" in w and "post_credit" in w:
        return (
            "Gaya Visual dan Apresiasi Penggemar",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton yang merayakan Spider-Verse sebagai tontonan yang menghadirkan kesenangan visual sekaligus memanjakan penggemar melalui easter eggs dan adegan post-credit. Kedua aspek ini saling memperkuat pengalaman.",
                f"'Animation_style', 'post_credit', 'comic_book', dan 'no_different' menunjukkan kombinasi antara apresiasi artistik dan fan service yang efektif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan penonton yang mengidentifikasi elemen fan service sebagai komponen yang menambah nilai.",
                "Spider-Verse berhasil memadukan inovasi artistik dengan apresiasi penggemar melalui referensi komik dan adegan post-credit yang memuaskan berbagai kalangan penonton."
            )
        )
    if "not_regret" in w or "never_seen" in w:
        return (
            "Melampaui Ekspektasi: Tidak Menyesal Menontonnya",
            build_notes(
                "Topik ini merepresentasikan respons penonton yang datang dengan ekspektasi rendah namun meninggalkan bioskop dengan kesan yang jauh melampaui antisipasi mereka. 'Not_regret' sebagai ekspresi kepuasan menjadi penanda semantik yang kuat.",
                f"'Not_regret', 'never_seen', 'super_hero', dan 'not_to' menunjukkan pola kepuasan yang lahir dari ekspektasi yang terlampaui. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa signifikan faktor 'ekspektasi terlampaui' dalam membentuk penilaian positif.",
                "Spider-Verse berhasil mengubah skeptisisme awal menjadi kepuasan mendalam, dengan mayoritas penonton menyatakan bahwa film ini jauh melampaui ekspektasi mereka."
            )
        )
    return (
        "Animasi Superhero yang Berbeda dari Biasa",
        build_notes(
            "Topik ini merepresentasikan penilaian umum penonton yang mengidentifikasi Spider-Verse sebagai film superhero yang berbeda secara fundamental dari formula yang sudah ada. Perbedaan ini dipandang positif sebagai inovasi.",
            f"Kombinasi kata-kata yang berkaitan dengan gaya animasi, karakter superhero, dan pembedaan dari norma menunjukkan identifikasi terhadap keunikan film. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menilai film terutama berdasarkan keunikannya dibandingkan karya sejenis.",
            "Spider-Verse diidentifikasi penonton sebagai anomali positif dalam genre film superhero yang membawa inovasi naratif dan visual yang signifikan."
        )
    )

def analyze_spiderverse_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "animation" in w and "comic" in w and "style" in w and "no_different" not in w:
        return (
            "Animasi Komik dan Revolusi Gaya Visual",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap pendekatan animasi Spider-Verse yang secara radikal berbeda dari film animasi konvensional. Gaya yang mereplikasi estetika buku komik cetak dipandang sebagai terobosan artistik yang mendefinisikan ulang standar industri.",
                f"'Animation', 'comic', 'book', 'style', dan 'dream' membentuk cluster estetika yang konsisten dan berpusat pada identitas visual. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan bahwa inovasi gaya animasi adalah aspek yang paling banyak diidentifikasi sebagai keunggulan utama.",
                "Gaya animasi Spider-Verse yang mereplikasi estetika buku komik cetak diakui penonton sebagai terobosan artistik yang mendefinisikan ulang standar film animasi kontemporer."
            )
        )
    if "no_different" in w or ("visuals" in w and "original" in w):
        return (
            "Orisinalitas Visual dalam Lanskap Superhero",
            build_notes(
                "Topik ini merepresentasikan penilaian penonton yang membandingkan Spider-Verse dengan film superhero lain dan mengidentifikasi orisinalitas visualnya sebagai pembeda yang signifikan. 'No_different' dalam konteks ini kemungkinan merujuk pada cara film ini berbeda dari yang sudah ada.",
                f"'No_different', 'visuals', 'original', dan 'fresh' menunjukkan evaluasi komparatif yang mengidentifikasi keunikan Spider-Verse dalam lanskap yang jenuh. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mencerminkan penonton yang secara eksplisit menggunakan kerangka komparatif dalam penilaian.",
                "Spider-Verse dinilai sebagai anomali orisinal dalam genre film superhero yang sudah jenuh, menghadirkan identitas visual dan naratif yang secara fundamental berbeda."
            )
        )
    if "marvel" in w or "storyline" in w or ("not_regret" in w and "heart" in w):
        return (
            "Kualitas Naratif di Balik Kecemerlangan Visual",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap kekuatan narasi Spider-Verse yang sering terabaikan di balik pujian visual. Struktur plot yang koheren, emosional, dan berhasil mengelola banyak versi karakter menjadi sorotan.",
                f"'Marvel', 'storyline', 'not_regret', dan 'heart' menunjukkan apresiasi terhadap substansi naratif, bukan hanya visual. Konteks Marvel menambahkan dimensi posisi film dalam ekosistem franchise. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan penonton yang menilai naratif sebagai komplemen esensial dari keunggulan visual.",
                "Spider-Verse diakui penonton memiliki kualitas naratif yang kuat sebagai fondasi yang menopang kecanggihan visualnya, menjadikannya lebih dari sekadar tontonan visual semata."
            )
        )
    if "uncle" in w or ("not_be" in w and "high" in w):
        return (
            "Kehilangan Uncle Aaron dan Beban Warisan",
            build_notes(
                "Topik ini merepresentasikan respons emosional penonton terhadap momen-momen kehilangan dalam Spider-Verse, khususnya kematian karakter yang berperan sebagai mentor Miles. Beban mewarisi identitas Spider-Man menjadi tema emosional yang diidentifikasi penonton.",
                f"'Uncle', 'not_be', 'high', 'hero', dan 'heart' menunjukkan fokus pada dimensi emosional pengembangan karakter Miles. Konsep mewarisi mantel superhero menjadi pusat diskusi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang terhubung secara emosional dengan arc karakter Miles.",
                "Momen kehilangan dan beban mewarisi identitas Spider-Man menjadi jangkar emosional Spider-Verse yang berhasil membuat penonton berinvestasi secara personal pada perjalanan Miles Morales."
            )
        )
    if "beautiful" in w and ("superhero" in w or "not_to" in w):
        return (
            "Keindahan Visual dan Daya Tarik Karakter",
            build_notes(
                "Topik ini merepresentasikan apresiasi estetis penonton terhadap kombinasi antara keindahan visual Spider-Verse dan daya tarik karakter-karakternya. Kedua aspek ini berfungsi secara sinergis dalam menciptakan pengalaman menonton yang menyenangkan.",
                f"'Beautiful', 'animation', 'superhero', 'awesome', dan 'not_to' menunjukkan respons estetis yang positif terhadap visual dan karakter. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mendekati film dari perspektif estetika dan daya tarik visual.",
                "Penonton mengapresiasi Spider-Verse sebagai karya yang berhasil memadukan keindahan visual yang memukau dengan karakter-karakter yang mudah dicintai dan diidentifikasi."
            )
        )
    if "expectation" in w or "not_regret" in w:
        return (
            "Ekspektasi Terlampaui dan Kepuasan Menonton",
            build_notes(
                "Topik ini merepresentasikan pola kepuasan penonton yang mengalami bahwa Spider-Verse secara konsisten melampaui ekspektasi mereka — terutama bagi penonton yang awalnya skeptis terhadap film animasi Spider-Man buatan Sony.",
                f"'Not_regret', 'expectation', 'superhero', dan 'beautiful' menunjukkan perbandingan antara antisipasi dan hasil. Pola ini sering disertai ekspresi kejutan positif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang secara aktif melaporkan pengalaman ekspektasi yang terlampaui.",
                "Konsistensi Spider-Verse dalam melampaui ekspektasi berbagai segmen penonton — termasuk yang skeptis — menjadi salah satu penanda keberhasilannya yang paling signifikan."
            )
        )
    if "never_seen" in w and "hero" in w:
        return (
            "Visi Heroisme yang Belum Pernah Ada",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap cara Spider-Verse mendefinisikan ulang konsep heroisme melalui Miles Morales. 'Anyone can wear the mask' bukan sekadar slogan, melainkan premis naratif yang dibuktikan melalui perjalanan karakter.",
                f"'Never_seen', 'hero', 'animation', 'awesome', dan 'idea' menunjukkan bahwa penonton mengidentifikasi Spider-Verse sebagai pembaruan konseptual terhadap mitos superhero. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan seberapa besar resonansi redefinisi heroisme dalam diskusi penonton.",
                "Spider-Verse menawarkan definisi baru tentang heroisme yang inklusif dan demokratis — bahwa siapapun dengan keberanian dan tanggung jawab bisa menjadi pahlawan."
            )
        )
    return (
        "Animasi Superhero sebagai Karya Sinema",
        build_notes(
            "Topik ini merepresentasikan penilaian umum penonton yang mengidentifikasi Spider-Verse sebagai film yang melampaui kategori 'animasi untuk anak-anak' dan mendudukinya sebagai karya sinema yang serius.",
            f"Kombinasi kata-kata yang berkaitan dengan animasi, superhero, dan keunikan menunjukkan penghargaan terhadap film sebagai medium artistik yang serius. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% mencerminkan pandangan penonton yang menolak kategorisasi simplisistik terhadap film animasi.",
            "Penonton menilai Spider-Verse sebagai karya sinema yang serius yang kebetulan berbentuk animasi, bukan sekadar film animasi yang kebetulan dinikmati orang dewasa."
        )
    )

# ── THE DARK KNIGHT (2008) ─────────────────────────────────────

def analyze_tdk_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "gary_oldman" in w and "human_nature" in w:
        return (
            "Eksplorasi Filosofis Sifat Manusia",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap dimensi filosofis The Dark Knight yang menggunakan konflik antar karakter sebagai medium eksplorasi tentang batas tipis antara kebaikan dan kejahatan. Film diidentifikasi sebagai lebih dari sekadar tontonan aksi.",
                f"'Gary_oldman', 'human_nature', 'no_doubt', dan 'special_effect' menunjukkan gabungan antara diskursus filosofis dan penilaian teknis. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mendekati film dari perspektif tematis dan filosofis.",
                "The Dark Knight menggunakan konflik Batman-Joker sebagai medium eksplorasi filosofis tentang sifat manusia, melampaui batas genre film superhero konvensional."
            )
        )
    if "jack_nicholson" in w and ("hero_villain" in w or "tommy_jones" in w):
        return (
            "Perbandingan Joker: Ledger vs. Nicholson",
            build_notes(
                "Topik ini merepresentasikan diskusi intertekstual penonton yang membandingkan penampilan Heath Ledger sebagai Joker dengan interpretasi pendahulunya. Perbandingan ini menjadi salah satu diskusi terpanjang dalam wacana film superhero.",
                f"'Jack_nicholson', 'hero_villain', 'harvey_dent', dan 'tommy_jones' menunjukkan kerangka komparatif lintas adaptasi. Konteks sejarah adaptasi Batman memperkaya diskusi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar proporsi diskusi yang menggunakan perbandingan lintas karya sebagai kerangka penilaian.",
                "Penampilan Heath Ledger sebagai Joker mendorong perbandingan lintas adaptasi yang kaya, dengan mayoritas penonton menyimpulkan bahwa interpretasi Ledger membawa dimensi psikologis yang belum pernah ada sebelumnya."
            )
        )
    if "michael_caine" in w and "morgan_freeman" in w and "aaron_eckhart" in w:
        return (
            "Keunggulan Ensemble Cast",
            build_notes(
                "Topik ini merepresentasikan penilaian penonton terhadap kualitas kolektif ensemble cast yang menjadi salah satu pilar keberhasilan The Dark Knight. Penampilan seluruh pemain dinilai secara bersamaan sebagai satu kesatuan yang kohesif.",
                f"'Christian_bale', 'michael_caine', 'morgan_freeman', 'gary_oldman', dan 'aaron_eckhart' membentuk inventarisasi ensemble yang komprehensif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan bahwa kualitas ensemble dinilai secara holistik, bukan hanya fokus pada satu karakter.",
                "Kekuatan kolektif ensemble cast The Dark Knight diidentifikasi sebagai komponen esensial yang memperkuat kredibilitas naratif di luar kegemilangan karakter Joker semata."
            )
        )
    if ("oscar_worthy" in w or "crime_drama" in w) and "hero_villain" in w:
        return (
            "Melampaui Superhero: Layak Penghargaan Utama",
            build_notes(
                "Topik ini merepresentasikan argumen penonton bahwa The Dark Knight melampaui batas genre superhero dan layak diperlakukan sebagai drama kriminal serius yang setara dengan karya terbaik yang pernah mendapat pengakuan Academy Awards.",
                f"'Oscar_worthy', 'crime_drama', 'hero_villain', dan 'comic_book' menunjukkan argumen tentang reklasifikasi film dari genre ke karya sinema serius. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar proporsi penonton yang mengidentifikasi film ini sebagai karya yang melampaui batasan genre.",
                "The Dark Knight dinilai melampaui kategori film superhero dan diposisikan penonton sebagai drama kriminal serius yang layak mendapat pengakuan akademis tertinggi."
            )
        )
    if "harvey_dent" in w and ("district_attorney" in w or "eckhart_harvey" in w or "installment_series" in w):
        return (
            "Busur Karakter Harvey Dent dan Two-Face",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap pengelolaan karakter Harvey Dent/Two-Face sebagai kontras moral yang kompleks terhadap Joker. Busur karakter Dent diidentifikasi sebagai komponen naratif yang memperkaya lapisan tematik film.",
                f"'Harvey_dent', 'district_attorney', 'eckhart_harvey', dan 'maggie_gyllenhaal' menunjukkan analisis karakter yang melampaui protagonis dan antagonis utama. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi Harvey Dent sebagai kunci naratif yang sering terabaikan.",
                "Transformasi Harvey Dent dari harapan Gotham menjadi Two-Face berfungsi sebagai argumen naratif terkuat bahwa kejahatan Joker berhasil menghancurkan lebih dari sekadar fisik."
            )
        )
    if "caine_morgan" in w or ("not_one" in w and "oscar_worthy" in w):
        return (
            "Peran Pendukung dan Fondasi Moral Batman",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap peran-peran pendukung — Alfred, Lucius Fox, Gordon — yang memberi dimensi kemanusiaan pada Bruce Wayne. Tanpa peran-peran ini, karakter Batman akan terasa terlalu abstrak dan tidak dapat dikaitkan.",
                f"'Caine_morgan', 'michael_caine', 'morgan_freeman', 'oscar_worthy', dan 'not_one' menunjukkan diskusi tentang kontribusi peran pendukung pada kohesi emosional film. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan penonton yang menghargai peran ensemble di luar spotlightnya.",
                "Alfred, Lucius Fox, dan Gordon tidak hanya berfungsi sebagai peran pendukung, tetapi sebagai fondasi moral yang memberi kemanusiaan pada sosok Batman."
            )
        )
    if "long_credit" in w and "crime_drama" in w:
        return (
            "Warisan Sinematik Film Kriminal Terbaik",
            build_notes(
                "Topik ini merepresentasikan diskusi tentang warisan jangka panjang The Dark Knight dalam sejarah sinema — khususnya posisinya dalam kanon drama kriminal yang melampaui konteks film superhero. Film dinilai sebagai karya yang akan terus relevan.",
                f"'Long_credit', 'crime_drama', 'harvey_dent', 'not_just', dan 'comic_book' menunjukkan diskursus tentang posisi film dalam narasi sejarah sinema. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang membingkai film dalam konteks warisan sinematik jangka panjang.",
                "The Dark Knight mengukuhkan dirinya sebagai salah satu drama kriminal terbaik dalam sejarah sinema, melampaui konteks dan batasan genre film superhero."
            )
        )
    if "installment_series" in w:
        return (
            "Puncak Trilogi Batman Nolan",
            build_notes(
                "Topik ini merepresentasikan penilaian The Dark Knight sebagai titik tertinggi dari trilogi Batman Christopher Nolan. Posisi film dalam konteks trilogi diidentifikasi sebagai faktor yang memperkuat penghargaan terhadapnya.",
                f"'Installment_series', 'oscar_worthy', 'harvey_dent', dan 'david_goyer' menunjukkan evaluasi film dalam konteks serial yang lebih panjang. Kontribusi penulis naskah David Goyer juga diakui. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar proporsi penonton yang mengevaluasi film dalam konteks triloginya.",
                "The Dark Knight dinilai sebagai puncak artistik dari trilogi Batman Nolan yang berhasil memenuhi janji dari pendahulunya sekaligus melampaui ekspektasi penerusnya."
            )
        )
    if "katie_holmes" in w or "rachel_dawes" in w:
        return (
            "Karakter Rachel Dawes dan Penilaian Pengecoran",
            build_notes(
                "Topik ini merepresentasikan diskusi penonton tentang karakter Rachel Dawes dan dampak pergantian aktris — dari Katie Holmes ke Maggie Gyllenhaal — terhadap konsistensi trilogi. Diskusi ini menyentuh isu yang lebih luas tentang pengelolaan franchise.",
                f"'Katie_holmes', 'rachel_dawes', 'maggie_gyllenhaal', dan 'christian_bale' menunjukkan diskursus tentang casting dan kontinuitas karakter. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mencerminkan seberapa besar perhatian penonton terhadap aspek casting dalam penilaian.",
                "Pergantian aktris untuk karakter Rachel Dawes menjadi topik diskusi penonton yang menyentuh isu lebih luas tentang pengelolaan karakter dalam konteks trilogi."
            )
        )
    return (
        "Penampilan Joker dan Akting Heath Ledger",
        build_notes(
            "Topik ini merepresentasikan apresiasi penonton terhadap penampilan Heath Ledger sebagai Joker — yang secara universal diakui sebagai salah satu penampilan terbaik dalam sejarah sinema. Fokus pada aktingnya mendominasi sebagian besar diskusi.",
            f"Kombinasi nama-nama aktor dengan kata kunci seperti 'oscar_worthy' dan 'human_nature' menunjukkan sentralitas penampilan Ledger dalam diskusi. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar proporsi diskusi yang berpusat pada penampilan Ledger.",
            "Penampilan Heath Ledger sebagai Joker mendominasi diskusi The Dark Knight sebagai salah satu pencapaian akting terbesar dalam sejarah genre superhero."
        )
    )

def analyze_tdk_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "no_doubt" in w and ("brilliant" in w or "dent" in w or "harvey" in w):
        return (
            "Mahakarya yang Tidak Terbantahkan",
            build_notes(
                "Topik ini merepresentasikan konsensus kuat penonton yang menyatakan The Dark Knight sebagai mahakarya tanpa reservasi. Ketidakterbantahan kualitasnya menjadi premis yang tidak lagi memerlukan argumentasi dalam ulasan-ulasan ini.",
                f"'No_doubt', 'brilliant', 'harvey', 'dent', dan 'christian' menunjukkan keyakinan penuh tanpa hedging. Ekspresi seperti 'no_doubt' secara eksplisit menolak potensi keberatan. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar proporsi penonton yang memberikan penilaian tertinggi tanpa kualifikasi.",
                "Penonton menyatakan dengan keyakinan penuh bahwa The Dark Knight adalah mahakarya sinematik yang tidak memerlukan pembelaan — sebuah penilaian yang tidak terbantahkan."
            )
        )
    if "imax" in w or ("comic" in w and "book" in w):
        return (
            "Estetika Komik dan Pengalaman IMAX",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap keputusan Nolan menggunakan kamera IMAX — yang berdampak langsung pada skala visual film — dan koneksinya dengan estetika buku komik yang menjadi sumber material.",
                f"'Comic', 'book', 'imax', 'eckhart', dan 'show' menunjukkan koneksi antara medium sumber (komik) dengan format produksi (IMAX). Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan penonton yang menghargai keputusan teknis produksi sebagai faktor penentu.",
                "Keputusan menggunakan kamera IMAX untuk merekam adegan kunci diidentifikasi sebagai salah satu faktor teknis yang paling berkontribusi pada skala sinematik The Dark Knight."
            )
        )
    if "superhero" in w and ("greatest" in w or "never_see" in w or "villain" in w):
        return (
            "Mendefinisikan Ulang Genre Superhero",
            build_notes(
                "Topik ini merepresentasikan argumen penonton yang menyatakan The Dark Knight telah mendefinisikan ulang apa yang mungkin dalam genre film superhero. Film ini menjadi referensi standar untuk diskusi tentang superhero yang 'serius'.",
                f"'Superhero', 'greatest', 'villain', 'christopher', dan 'never_see' menunjukkan penilaian komparatif yang menempatkan film ini di posisi puncak. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang secara aktif mendorong argumen tentang redefinisi genre.",
                "The Dark Knight secara konsensual diidentifikasi penonton sebagai film yang telah mendefinisikan ulang standar dan ambisi genre film superhero secara permanen."
            )
        )
    if "perfect" in w and ("bale" in w or "christopher" in w):
        return (
            "Kolaborasi Sempurna: Nolan dan Bale",
            build_notes(
                "Topik ini merepresentasikan penilaian atas sinergi antara visi sutradara Christopher Nolan dan interpretasi Christian Bale sebagai Batman. Keduanya dipandang sebagai kolaborasi yang menghasilkan versi Batman paling definitif.",
                f"'Perfect', 'bale', 'christopher', dan 'excellent' menunjukkan evaluasi integratif terhadap dua kontribusi utama. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa sering penonton mengidentifikasi kolaborasi sutradara-aktor sebagai faktor penentu.",
                "Sinergi antara visi Christopher Nolan dan penampilan Christian Bale dipandang sebagai kolaborasi yang menghasilkan interpretasi Batman paling komprehensif yang pernah ada."
            )
        )
    if ("fantastic" in w or "awesome" in w) and "city" in w:
        return (
            "Gotham sebagai Kota yang Nyata dan Terancam",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap keberhasilan Nolan membuat Gotham terasa seperti kota nyata yang benar-benar dalam ancaman — bukan kota komik imajinatif. Keputusan memfilmkan Chicago sebagai Gotham berkontribusi signifikan.",
                f"'Fantastic', 'city', 'bale', 'awesome', dan 'dent' menunjukkan koneksi antara setting urban yang realistis dengan ketegangan naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang secara khusus mengidentifikasi presentasi Gotham sebagai kekuatan film.",
                "Gotham dalam The Dark Knight berfungsi bukan hanya sebagai latar, melainkan sebagai karakter otonom yang terasa nyata dan rentan terhadap kekacauan yang dilancarkan Joker."
            )
        )
    if "oscar" in w and ("not_sure" in w or "superhero" in w):
        return (
            "Kelayakan Oscar dan Bias Genre",
            build_notes(
                "Topik ini merepresentasikan diskusi tentang kegagalan The Dark Knight mendapatkan nominasi Oscar Best Picture dan implikasinya terhadap bias historis Academy Awards terhadap genre populer. Kekecewaan ini mendorong perubahan kebijakan Academy.",
                f"'Oscar', 'not_sure', 'superhero', dan 'perfect' menunjukkan diskursus meta tentang industri penghargaan. Referensi historis tentang ekspansi nominasi Best Picture relevan di sini. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa signifikan isu penghargaan dalam wacana kritis penonton.",
                "Kegagalan The Dark Knight mendapatkan nominasi Oscar Best Picture menjadi katalis diskusi tentang bias historis Academy Awards terhadap genre populer."
            )
        )
    if "villain" in w and ("city" in w or "not_seen" in w):
        return (
            "Joker sebagai Kekuatan Destruktif Kota",
            build_notes(
                "Topik ini merepresentasikan analisis penonton terhadap Joker bukan sebagai penjahat konvensional yang menginginkan kekayaan atau kekuasaan, melainkan sebagai kekuatan ideologis yang bertujuan membuktikan bahwa setiap manusia dapat direduksi menjadi kaos.",
                f"'Villain', 'city', 'not_seen', dan 'christopher' menunjukkan analisis terhadap motivasi dan fungsi naratif karakter antagonis. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan penonton yang menganalisis Joker pada level ideologis.",
                "Joker dianalisis penonton sebagai representasi ideologi kekacauan yang lebih menakutkan dari penjahat konvensional karena bukan keuntungan material yang ia cari."
            )
        )
    if "credit" in w and ("christopher" in w or "special" in w):
        return (
            "Sinematografi dan Kedetailan Teknis",
            build_notes(
                "Topik ini merepresentasikan apresiasi teknis penonton terhadap detail sinematografi The Dark Knight — termasuk karya Wally Pfister yang kemudian mendapat pengakuan Oscar. Setiap keputusan teknis dipandang sebagai yang disengaja dan bermakna.",
                f"'Credit', 'special', 'christopher', 'bale', dan 'cinematography' menunjukkan evaluasi berbasis analisis teknis. Kontribusi Pfister sering menjadi rujukan spesifik. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengevaluasi film dari perspektif teknis sinematografis.",
                "Sinematografi Wally Pfister dan keputusan teknis produksi lainnya diidentifikasi penonton sebagai komponen yang mengelevasi The Dark Knight ke level karya sinema yang ambisius."
            )
        )
    if "crime" in w or "series" in w:
        return (
            "Ekosistem Kriminal Gotham dan Serialitas",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap kedalaman ekosistem kriminal Gotham yang dibangun Nolan — di mana setiap karakter dan fraksi memiliki motivasi yang kohesif dalam sistem sosial yang kompleks.",
                f"'Crime', 'series', 'city', 'bale', dan 'christopher' menunjukkan perspektif yang memandang film sebagai sistem naratif yang kompleks, bukan sekadar plot tunggal. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan penonton yang menganalisis film sebagai ekosistem naratif yang organik.",
                "The Dark Knight membangun ekosistem kriminal Gotham yang terasa organis dan memiliki logika internalnya sendiri, menghasilkan ketegangan naratif yang jauh lebih meyakinkan dari film superhero konvensional."
            )
        )
    return (
        "Dampak Sinematik yang Bertahan Lama",
        build_notes(
            "Topik ini merepresentasikan penilaian tentang warisan jangka panjang The Dark Knight sebagai film yang terus relevan dan sering dirujuk sebagai standar dalam diskusi tentang film superhero.",
            f"Kombinasi kata-kata evaluatif menunjukkan penilaian holistik. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% mencerminkan penilaian komprehensif terhadap warisan film.",
            "The Dark Knight meninggalkan dampak sinematik yang bertahan lama, terus menjadi rujukan standar dalam setiap diskusi tentang potensi artistik film superhero."
        )
    )

# ── LOTR: RETURN OF THE KING (2003) ───────────────────────────

def analyze_lotr_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "greatest_trilogy" in w and ("middle_earth" in w or "extended_edition" in w):
        return (
            "Middle-Earth dan Trilogi Terbesar Sinema",
            build_notes(
                "Topik ini merepresentasikan konsensus penonton yang menempatkan trilogi LOTR — dan Return of the King sebagai puncaknya — dalam posisi tertinggi dalam sejarah film epik. Middle-Earth sebagai dunia fiksi dinilai sebagai realisasi world-building paling komprehensif yang pernah ada.",
                f"'Middle_earth', 'greatest_trilogy', 'extended_edition', dan 'dark_sauron' menunjukkan evaluasi yang melampaui film tunggal menuju konteks trilogi dan dunia fiksinya secara keseluruhan. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mendekati film dalam konteks triloginya.",
                "Penonton menempatkan Return of the King sebagai puncak dari apa yang secara luas diakui sebagai trilogi film terbaik yang pernah diproduksi, dengan Middle-Earth sebagai dunia fiksi paling terealisasi dalam sejarah sinema."
            )
        )
    if "read_book" in w and ("tolkien_fan" in w or "sean_astin" in w):
        return (
            "Adaptasi Buku dan Sudut Pandang Penggemar Tolkien",
            build_notes(
                "Topik ini merepresentasikan perspektif penonton yang sebelumnya membaca novel Tolkien dan mengevaluasi adaptasi Jackson dari sudut pandang kesetiaan terhadap sumber material. Evaluasi ini biasanya lebih nuanced dan analitis.",
                f"'Read_book', 'tolkien_fan', 'sean_astin', 'aragorn_viggo', dan 'comic_relief' menunjukkan kerangka evaluasi berbasis pengetahuan sumber material. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengevaluasi adaptasi dari perspektif pembaca novel.",
                "Penonton yang sebelumnya membaca novel Tolkien mengevaluasi Return of the King melalui lensa kesetiaan adaptasi, mengidentifikasi keberhasilan dan kompromi yang dibuat Jackson."
            )
        )
    if "final_battle" in w and "viggo_mortensen" in w:
        return (
            "Pertempuran Epik dan Inovasi Efek Visual",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap sekuens pertempuran Return of the King yang mendefinisikan ulang standar sinema kolosal. Penggunaan sistem Massive untuk mensimulasikan ribuan tentara digital menjadi tonggak sejarah teknologi film.",
                f"'Special_effect', 'final_battle', 'viggo_mortensen', dan 'source_material' menunjukkan koneksi antara pencapaian teknis dengan presisi adaptasi sumber material. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan seberapa besar apresiasi terhadap pencapaian teknis pertempuran dalam penilaian penonton.",
                "Sekuens pertempuran dalam Return of the King mendefinisikan ulang standar sinema kolosal melalui inovasi teknis yang belum pernah dicapai sebelumnya."
            )
        )
    if "giant_spider" in w or "final_chapter" in w:
        return (
            "Momen Klimaks dan Penutup Emosional",
            build_notes(
                "Topik ini merepresentasikan respons penonton terhadap momen-momen klimaktis Return of the King — dari pertempuran Shelob hingga kehancuran Cincin Satu di Gunung Doom — sebagai puncak emosional yang memuaskan sebuah narasi panjang.",
                f"'Giant_spider', 'final_chapter', 'never_been', dan 'perfect_perfect' menunjukkan identifikasi terhadap momen-momen puncak naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang fokus pada momen-momen klimaktis sebagai ukuran kepuasan.",
                "Momen-momen klimaktis Return of the King — dari Shelob hingga Mount Doom — berfungsi sebagai puncak emosional yang memberikan kepuasan proporsional terhadap investasi tiga film."
            )
        )
    if "academy_award" in w or "trilogy_favourite" in w:
        return (
            "Penghargaan Oscar dan Warisan Sinematik",
            build_notes(
                "Topik ini merepresentasikan diskusi tentang kemenangan bersejarah 11 Oscar Return of the King dan posisinya dalam sejarah sinema. Penghargaan ini dipandang sebagai pengakuan kumulatif atas keseluruhan trilogi.",
                f"'Academy_award', 'viggo_mortensen', 'greatest_trilogy', dan 'trilogy_favourite' menunjukkan diskursus tentang pengakuan institusional dan warisan kultural. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mencerminkan seberapa besar dimensi penghargaan masuk dalam penilaian penonton.",
                "Kemenangan 11 Oscar Return of the King dianggap sebagai pengakuan retrospektif atas keseluruhan pencapaian trilogi, bukan hanya film ketiga semata."
            )
        )
    if "not_this" in w or "john_noble" in w:
        return (
            "Catatan Kritis terhadap Pilihan Adaptasi",
            build_notes(
                "Topik ini merepresentasikan pandangan penonton yang menyertakan reservasi spesifik terhadap beberapa keputusan adaptasi Jackson. Kritik ini sering terfokus pada karakter atau sekuens yang dianggap tidak sesuai dengan sumber material.",
                f"'Not_this', 'john_noble', 'comic_relief', dan 'mount_doom' menunjukkan identifikasi terhadap elemen-elemen yang dianggap kurang berhasil. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menyertakan perspektif kritis dalam penilaian.",
                "Sebagian penonton mengidentifikasi keputusan adaptasi tertentu yang dianggap tidak optimal, terutama berkaitan dengan tonalitas beberapa karakter yang terasa tidak konsisten."
            )
        )
    if "fellowship_tower" in w and ("source_material" in w or "dark_sauron" in w):
        return (
            "Kesinambungan Trilogi dan Kesetiaan Material",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap kemampuan Jackson mempertahankan benang merah naratif dari Fellowship of the Ring hingga Return of the King, sambil tetap setia terhadap esensi sumber material Tolkien.",
                f"'Fellowship_tower', 'source_material', 'tolkien_book', dan 'dark_sauron' menunjukkan perspektif yang menilai film dalam konteks kesinambungan trilogi dan relasi dengan sumber material. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mencerminkan penonton yang mengevaluasi kohesi naratif lintas tiga film.",
                "Jackson berhasil mempertahankan kesinambungan naratif yang kohesif sepanjang trilogi sambil menjaga esensi dari sumber material Tolkien yang kaya."
            )
        )
    return (
        "Puncak Sinema Fantasi Epik",
        build_notes(
            "Topik ini merepresentasikan penilaian umum penonton yang menempatkan Return of the King sebagai puncak dari genre fantasi epik dalam sejarah sinema. Komponen teknis, naratif, dan emosional dinilai secara holistik.",
            f"Kombinasi kata-kata tentang Middle-Earth, special effects, dan karakter menunjukkan penilaian komprehensif. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi ulasan dengan evaluasi menyeluruh.",
            "Return of the King diidentifikasi sebagai puncak genre fantasi epik dalam sejarah sinema, melampaui standar yang ada melalui integrasi world-building, aksi, dan emosi."
        )
    )

def analyze_lotr_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "tolkien" in w and ("tower" in w or "fellowship" in w or "novel" in w):
        return (
            "Warisan Tolkien dan Tanggung Jawab Adaptasi",
            build_notes(
                "Topik ini merepresentasikan diskusi tentang dimensi literatur dari Return of the King — bagaimana Jackson mengemban tanggung jawab mengadaptasi karya sastra yang sudah memiliki audiens setia selama puluhan tahun.",
                f"'Tolkien', 'trilogy', 'tower', 'fellowship', dan 'novel' menunjukkan kerangka evaluasi berbasis literatur. Bobot warisan Tolkien dalam penilaian tercermin dari frekuensi kemunculan namanya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar dimensi literatur masuk dalam diskusi penonton.",
                "Warisan sastra Tolkien memberikan konteks evaluatif yang unik bagi penonton yang menilai Return of the King bukan hanya sebagai film, tetapi sebagai adaptasi dari mitologi yang sudah dicintai."
            )
        )
    if "conclusion" in w and ("special" in w or "perfect" in w):
        return (
            "Penutup Trilogi yang Sempurna",
            build_notes(
                "Topik ini merepresentasikan penilaian positif terhadap Return of the King sebagai penutup yang memenuhi ekspektasi tinggi dari trilogi yang luar biasa. Kepuasan atas resolusi naratif menjadi tema sentral.",
                f"'Trilogy', 'conclusion', 'special', dan 'tolkien' menunjukkan kerangka penilaian berbasis kepuasan penutup naratif. Konteks trilogi memberikan standar yang perlu dipenuhi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mencerminkan konsensus penonton tentang keberhasilan film sebagai penutup.",
                "Return of the King berhasil memberikan penutup yang memuaskan bagi trilogi dengan standar yang sangat tinggi, menyelesaikan ketiga benang naratif utama dengan cara yang dianggap proporsional dan bermartabat."
            )
        )
    if "gollum" in w and ("effect" in w or "final" in w) and "brilliant" not in w:
        return (
            "Gollum dan Pertempuran Kolosal",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap dua pencapaian teknis utama Return of the King: karakter CGI Gollum yang terasa nyata dan pertempuran berskala kolosal. Keduanya dipandang sebagai tonggak dalam sejarah efek visual.",
                f"'Gollum', 'battle', 'effect', dan 'final' menunjukkan identifikasi terhadap pencapaian teknis sebagai elemen yang paling berkesan. Kontribusi Andy Serkis sering menjadi diskusi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar apresiasi teknis mendominasi dalam penilaian.",
                "Karakter Gollum dan pertempuran kolosal Return of the King mewakili dua pencapaian teknis terbesar yang mendefinisikan ulang standar efek visual dalam sinema."
            )
        )
    if ("fan" in w or "intensity" in w) and "book" in w:
        return (
            "Intensitas untuk Fans dan Tantangan Aksesibilitas",
            build_notes(
                "Topik ini merepresentasikan diskusi tentang perbedaan pengalaman antara penggemar berat yang telah mengikuti seluruh trilogi dan penonton baru yang mungkin merasakan barrier aksesibilitas naratif.",
                f"'Fan', 'book', 'intensity', 'not_a', dan 'godfather' menunjukkan kesadaran tentang perbedaan pengalaman berdasarkan konteks sebelumnya. Referensi ke The Godfather menunjukkan upaya komparasi dengan masterpiece lain. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan diskusi tentang aksesibilitas dan kurva pembelajaran bagi penonton baru.",
                "Return of the King menawarkan intensitas emosional yang paling dapat diapresiasi oleh mereka yang telah mengikuti keseluruhan trilogi, sementara penonton baru mungkin merasakan barrier naratif."
            )
        )
    if "sauron" in w or ("not_perfect" in w and "viggo" in w):
        return (
            "Ketidaksempurnaan yang Dapat Diterima",
            build_notes(
                "Topik ini merepresentasikan pandangan penonton yang mengakui adanya aspek yang bisa lebih baik — dari multiple endings yang terasa berlebihan hingga beberapa efek yang kurang mulus — namun tetap menilai keseluruhan pencapaian dengan sangat tinggi.",
                f"'Sauron', 'not_perfect', 'gollum', 'viggo', dan 'not_been' menunjukkan kedewasaan penilaian yang mengakui kekurangan tanpa menggunakannya untuk mendiskualifikasi film. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mencerminkan penonton yang memberikan penilaian bernuansa dan realistis.",
                "Penonton mengakui ketidaksempurnaan tertentu dalam Return of the King namun menilai bahwa pencapaian keseluruhan jauh melampaui kekurangan-kekurangan tersebut."
            )
        )
    if "viggo" in w and ("without_him" in w or "excellent" in w):
        return (
            "Perjalanan Aragorn dan Viggo Mortensen",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap penyelesaian busur karakter Aragorn dan performa Viggo Mortensen yang membuat transformasi dari pengembara menjadi raja terasa autentik dan earned.",
                f"'Viggo', 'without_him', 'excellent', dan 'not_be' menunjukkan atribusi terhadap performa individual sebagai elemen kunci. Kontrafaktual 'without_him' memperkuat signifikansi kontribusinya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan penonton yang mengidentifikasi performa Viggo Mortensen sebagai komponen esensial.",
                "Viggo Mortensen membawa kedalaman psikologis pada karakter Aragorn yang membuat transformasinya dari pengembara menjadi raja terasa autentik dan memuaskan secara naratif."
            )
        )
    if "gollum" in w and ("brilliant" in w or "friendship" in w or "magical" in w):
        return (
            "Gollum sebagai Terobosan Akting Digital",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap karakter Gollum sebagai pencapaian paling signifikan dalam perpaduan akting dan teknologi — yang memperkenalkan teknik motion capture sebagai medium akting yang legitimate.",
                f"'Gollum', 'brilliant', 'friendship', 'magical', dan 'series' menunjukkan pengakuan terhadap orisinalitas dan resonansi emosional karakter CGI. Kontribusi Andy Serkis diakui sebagai akting sejati. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menilai Gollum sebagai pencapaian kreatif tertinggi film.",
                "Karakter Gollum mewakili terobosan dalam perpaduan akting motion capture dengan teknologi CGI, menghasilkan entitas fiksi yang memiliki kedalaman psikologis selayaknya karakter akting nyata."
            )
        )
    if "mina" in w or ("battle" in w and "emotional" in w):
        return (
            "Pertempuran Minas Tirith dan Dampak Emosional",
            build_notes(
                "Topik ini merepresentasikan respons penonton terhadap momen paling epik sekaligus paling mengharukan Return of the King — pertempuran di Minas Tirith yang menggabungkan skala sinema kolosal dengan muatan emosional karakter yang mendalam.",
                f"'Mina', 'battle', 'emotional', dan 'tolkien' menunjukkan koneksi antara spektakel sinematik dan resonansi emosional. Pertempuran ini juga dikenal sebagai salah satu yang paling kompleks dalam sejarah produksi film. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menilai pertempuran Minas Tirith sebagai puncak sinematik film.",
                "Pertempuran Minas Tirith berhasil mengintegrasikan skala sinema kolosal dengan muatan emosional karakter yang mendalam, menciptakan momen sinematik yang paling berkesan dalam sejarah trilogi."
            )
        )
    return (
        "Efek Visual dan Struktur Naratif Epik",
        build_notes(
            "Topik ini merepresentasikan penilaian umum terhadap kualitas teknis dan naratif Return of the King sebagai penutup dari trilogi epik.",
            f"Kombinasi kata-kata tentang efek, pertempuran, dan narasi menunjukkan penilaian komprehensif. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% mencerminkan evaluasi menyeluruh.",
            "Return of the King dinilai sebagai puncak dari trilogi yang berhasil mengintegrasikan efek visual dan struktur naratif epik secara harmonis."
        )
    )

# ── TOY STORY (1995) ───────────────────────────────────────────

def analyze_toystory_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "never_fails" in w and ("pizza_planet" in w or "randy_newman" in w):
        return (
            "Nostalgia Abadi yang Tidak Pernah Gagal",
            build_notes(
                "Topik ini merepresentasikan daya tahan Toy Story sebagai film yang relevan dan menyentuh di setiap penayangan ulang. 'Never_fails' sebagai ekspresi kepastian menunjukkan konsistensi respons emosional terhadap film.",
                f"'Never_fails', 'pizza_planet', 'randy_newman', 'theme_jealousy', dan 'feature_length' menunjukkan identifikasi terhadap elemen-elemen spesifik yang menginduksi nostalgia. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi Toy Story sebagai comfort film yang timeless.",
                "Toy Story memiliki kualitas timeless yang memastikan film ini tetap menyentuh dan relevan pada setiap penayangan ulang, lintas generasi dan konteks."
            )
        )
    if "computer_animation" in w and ("full_length" in w or "john_lasseter" in w) and "industry" not in w:
        return (
            "Terobosan Animasi Komputer John Lasseter",
            build_notes(
                "Topik ini merepresentasikan penilaian historis terhadap Toy Story sebagai film animasi komputer penuh pertama yang merevolusi industri. Kontribusi John Lasseter sebagai sutradara diidentifikasi sebagai faktor kunci keberhasilan.",
                f"'Computer_animation', 'full_length', 'john_lasseter', 'voice_talent', dan 'randy_newman' menunjukkan atribusi terhadap inovasi teknis dan artistik. Konteks historis sebagai 'pertama' memperkuat signifikansinya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar kesadaran historis memengaruhi penilaian penonton.",
                "Toy Story diakui sebagai tonggak bersejarah dalam industri animasi, di mana inovasi teknis John Lasseter membuka era baru yang mengubah lanskap produksi animasi selamanya."
            )
        )
    if "next_door" in w or "no_gift" in w:
        return (
            "Antagonis Sid dan Kedalaman Naratif",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap kompleksitas naratif Toy Story yang melampaui persaingan Woody-Buzz, termasuk dimensi Sid Phillips sebagai antagonis yang berfungsi sebagai refleksi tentang bagaimana mainan diperlakukan.",
                f"'Next_door', 'no_gift', 'john_lasseter', 'pizza_planet', dan 'disney_hand' menunjukkan perhatian terhadap detail naratif yang sering terabaikan. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menghargai kedalaman naratif di luar kisah utama.",
                "Kompleksitas naratif Toy Story melampaui konflik sentral, dengan elemen-elemen seperti karakter Sid Phillips menambahkan lapisan makna yang memperkaya pengalaman menonton."
            )
        )
    if "disney_hand" in w or ("animation_industry" in w and "adult_joke" in w):
        return (
            "Warisan Disney-Pixar dan Terobosan Industri",
            build_notes(
                "Topik ini merepresentasikan penilaian Toy Story dalam konteks dampaknya terhadap industri animasi secara keseluruhan. Film ini bukan hanya menghibur, melainkan secara literal mengubah cara animasi diproduksi dan dikonsumsi.",
                f"'Disney_hand', 'animation_industry', 'computer_animation', 'never_been', dan 'adult_joke' menunjukkan diskursus tentang dampak industri dan inovasi format. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mendekati film dari sudut pandang signifikansi industri.",
                "Toy Story bukan hanya film ikonik, tetapi merupakan katalis yang mengubah paradigma produksi animasi secara global dan membangun fondasi model bisnis Pixar-Disney."
            )
        )
    if "space_ranger" in w or "cowboy_doll" in w:
        return (
            "Konflik Identitas Woody dan Buzz",
            build_notes(
                "Topik ini merepresentasikan analisis terhadap tema sentral Toy Story — persaingan dan cemburu yang berkembang menjadi persahabatan. Konflik antara 'cowboy lama' dan 'space ranger baru' berfungsi sebagai metafora tentang krisis identitas dan ketakutan kehilangan relevansi.",
                f"'Space_ranger', 'cowboy_doll', 'theme_jealousy', 'animation_history', dan 'lightyear_space' menunjukkan identifikasi terhadap konflik karakter dan lapisan tematiknya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar konflik karakter diidentifikasi sebagai inti tematis film.",
                "Persaingan antara Woody dan Buzz berfungsi sebagai metafora universal tentang krisis identitas dan ketakutan kehilangan relevansi yang beresonansi dengan penonton dari berbagai usia."
            )
        )
    if "kid_adult" in w or "lightyear_allen" in w or "sheriff_hank" in w:
        return (
            "Daya Tarik Universal untuk Semua Usia",
            build_notes(
                "Topik ini merepresentasikan kemampuan Toy Story menyajikan konten yang bermakna bagi penonton anak-anak dan dewasa secara bersamaan melalui lapisan naratif yang berbeda namun sama-sama valid.",
                f"'Kid_adult', 'lightyear_allen', 'sheriff_hank', 'child_adult', dan 'voice_hank' menunjukkan identifikasi eksplisit terhadap dual audience. Pengisi suara Tom Hanks dan Tim Allen berkontribusi pada daya tarik ini. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang secara aktif mengidentifikasi multi-level appeal sebagai kekuatan.",
                "Toy Story berhasil menjangkau penonton anak-anak dan dewasa secara bersamaan melalui lapisan makna yang berbeda namun sama-sama bermakna dalam satu narasi yang terpadu."
            )
        )
    if "animation_industry" in w and "attention_detail" in w:
        return (
            "Keunggulan Teknis dan Perhatian Detail",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap perfeksionisme Pixar dalam membangun dunia Toy Story — dari tekstur permukaan hingga interaksi cahaya — yang secara kolektif menciptakan ilusi realitas yang meyakinkan.",
                f"'Animation_industry', 'attention_detail', 'computer_animation', 'never_seen', dan 'no_matter' menunjukkan evaluasi teknis yang mengidentifikasi detail sebagai komponen esensial. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan penonton yang menghargai kualitas teknis sebagai komponen yang membentuk pengalaman.",
                "Perfeksionisme Pixar dalam setiap detail visual Toy Story menciptakan ilusi realitas yang meyakinkan, menetapkan standar teknis yang menjadi patokan bagi industri animasi selanjutnya."
            )
        )
    return (
        "Terobosan Animasi dan Kualitas Produksi",
        build_notes(
            "Topik ini merepresentasikan penilaian umum terhadap kualitas produksi Toy Story sebagai film animasi yang melampaui standar zamannya.",
            f"Kombinasi kata-kata teknis dan artistik menunjukkan penilaian komprehensif. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi ulasan dengan penilaian holistik.",
            "Toy Story mendefinisikan standar baru dalam kualitas produksi animasi yang menjadi fondasi bagi perkembangan industri animasi digital selanjutnya."
        )
    )

def analyze_toystory_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "animation" in w and "computer" in w and "life" in w and "human" in w and "voice" not in w:
        return (
            "Teknologi Animasi dan Kisah Kemanusiaan",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap paradoks Toy Story — film yang menggunakan teknologi paling mutakhir pada zamannya untuk menceritakan kisah yang paling fundamental tentang kemanusiaan: persahabatan, cemburu, dan harga diri.",
                f"'Animation', 'computer', 'life', dan 'human' menunjukkan koneksi antara medium teknologi dengan konten kemanusiaan. Konteks historis sebagai pelopor animasi komputer memperkuat relevansinya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan penonton yang menghargai ironi produktif ini sebagai kekuatan.",
                "Toy Story memanfaatkan teknologi animasi komputer yang revolusioner bukan untuk menampilkan kemewahan visual, melainkan untuk menceritakan kisah manusiawi yang paling fundamental."
            )
        )
    if "adult" in w and ("kid" in w or "child" in w) and "voice" in w:
        return (
            "Humor Berlapis untuk Semua Demografi",
            build_notes(
                "Topik ini merepresentasikan kemampuan Toy Story menyajikan komedi dengan lapisan berbeda untuk penonton dari berbagai usia. Humor yang mengundang tawa anak-anak atas insiden fisik berbeda dari humor satiris yang diapresiasi penonton dewasa.",
                f"'Adult', 'kid', 'voice', 'funny', dan 'child' menunjukkan identifikasi terhadap strategi komedi berlapis. Performa pengisi suara Tom Hanks dan Tim Allen disebutkan dalam konteks ini. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan seberapa besar efektivitas humor berlapis dalam membentuk pengalaman menonton.",
                "Strategi komedi berlapis Toy Story berhasil menghadirkan tawa yang berbeda bagi penonton anak-anak dan dewasa secara bersamaan tanpa mengkompromikan integritas narasi."
            )
        )
    if "friendship" in w and ("brilliant" in w or "relatable" in w or "heart" in w):
        return (
            "Persahabatan Tulus yang Lahir dari Konflik",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap busur emosional inti Toy Story — bagaimana persahabatan Woody dan Buzz berkembang secara organis dari konflik dan permusuhan menuju rasa saling menghargai yang tulus.",
                f"'Friendship', 'brilliant', 'heart', dan 'relatable' menunjukkan resonansi emosional terhadap arc karakter. Kualitas 'relatable' menunjukkan bahwa penonton mengidentifikasi pengalaman mereka sendiri dalam narasi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar tema persahabatan beresonansi dalam diskusi penonton.",
                "Persahabatan Woody dan Buzz yang tumbuh dari konflik menjadi ikatan yang tulus beresonansi secara universal karena mencerminkan dinamika hubungan manusiawi yang nyata."
            )
        )
    if "disney" in w and ("family" in w or "no_one" in w or "no_gift" in w):
        return (
            "Warisan Disney dan Hiburan Keluarga",
            build_notes(
                "Topik ini merepresentasikan posisi Toy Story dalam tradisi panjang film keluarga Disney — sebagai penerus yang memperbarui formula sambil mempertahankan nilai-nilai inti tentang kebersamaan dan pertualangan.",
                f"'Disney', 'family', 'no_one', 'no_gift', dan 'never_fails' menunjukkan identifikasi terhadap konteks institusional Disney dalam membentuk pengalaman. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan penonton yang mendekati film dalam konteks tradisi Disney.",
                "Toy Story menempatkan dirinya dalam tradisi film keluarga Disney sambil membawa pembaruan formatif melalui teknologi dan sensibilitas naratif yang lebih modern."
            )
        )
    if "simple" in w or ("computer" in w and "animation" in w and "human" in w and "kind" in w):
        return (
            "Kesederhanaan Premis dan Kekuatan Naratif",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap keputusan Pixar yang tidak memperumit premis Toy Story — kesederhanaan 'bagaimana jika mainan hidup?' menjadi fondasi yang cukup kuat untuk menopang narasi yang kompleks secara emosional.",
                f"'Simple', 'animation', 'computer', 'human', dan 'kind' menunjukkan identifikasi terhadap kekuatan premis sederhana. Kontras antara kesederhanaan konsep dan kedalaman eksekusi menjadi objek apresiasi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mencerminkan penonton yang menghargai keeleganan premis sebagai kekuatan.",
                "Kesederhanaan premis Toy Story terbukti menjadi kekuatan bukan kelemahan — fondasi yang cukup solid untuk menopang narasi yang secara emosional jauh lebih kompleks."
            )
        )
    if "enjoyable" in w or ("not_to" in w and "voice" in w):
        return (
            "Film yang Menyenangkan untuk Ditonton Berulang",
            build_notes(
                "Topik ini merepresentasikan kualitas Toy Story sebagai film yang tetap memberikan kesenangan pada setiap penayangan ulang — sebuah pencapaian yang jarang dapat dipertahankan film dari era manapun.",
                f"'Enjoyable', 'voice', 'adult', 'animation', dan 'not_to' menunjukkan penilaian tentang kualitas hiburan yang bertahan. Ini berbeda dari penilaian tentang signifikansi artistik atau historis. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan proporsi penonton yang menilai film dari sudut pandang pure entertainment value.",
                "Toy Story mempertahankan kualitas hiburannya pada setiap penayangan ulang — sebuah pencapaian timelessness yang menandakan kekuatan fundamental naratif dan karakternya."
            )
        )
    if "never_fails" in w or "no_gift" in w:
        return (
            "Hadiah Lintas Generasi yang Tak Lekang Waktu",
            build_notes(
                "Topik ini merepresentasikan Toy Story sebagai karya yang diturunkan dari satu generasi ke generasi berikutnya — sebuah pengalaman berbagi yang menjadikan film bagian dari memori kolektif lintas keluarga.",
                f"'Never_fails', 'no_gift', 'disney', dan 'nor_monsters' menunjukkan dimensi warisan dan pengalaman berbagi antargenerasi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar dimensi lintas generasi menjadi bagian dari penilaian.",
                "Toy Story telah menjadi warisan budaya yang diturunkan antargenerasi, menjadikannya lebih dari sekadar film — melainkan bagian dari pengalaman berbagi yang mendefinisikan masa kecil banyak orang."
            )
        )
    if "friendship" in w and "hank" in w:
        return (
            "Resolusi Emosional: Ego yang Dikalahkan Persahabatan",
            build_notes(
                "Topik ini merepresentasikan momen katarsis Toy Story — ketika Woody akhirnya melepaskan egonya dan memilih bekerja sama dengan Buzz. Resolusi ini memberikan kepuasan naratif yang earned melalui konflik yang dibangun secara bertahap.",
                f"'Friendship', 'hank', 'heart', dan 'no_matter' menunjukkan identifikasi terhadap momen resolusi emosional sebagai puncak naratif. Konteks 'hank' sebagai singkatan nama tokoh memperkuat spesifisitas. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi resolusi emosional sebagai komponen paling memuaskan.",
                "Momen Woody melepaskan egonya demi Buzz memberikan kepuasan naratif yang earned dan menjadi inti pesan Toy Story tentang kebersamaan yang mengalahkan persaingan."
            )
        )
    return (
        "Kualitas Animasi dan Daya Tarik Universal",
        build_notes(
            "Topik ini merepresentasikan penilaian umum terhadap kualitas animasi dan daya tarik universal Toy Story yang menjadi fondasi reputasinya.",
            f"Kombinasi kata-kata tentang animasi dan kehidupan menunjukkan evaluasi holistik. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penilaian yang bersifat menyeluruh.",
            "Toy Story mempertahankan posisinya sebagai karya animasi dengan kualitas teknis dan daya tarik universal yang melampaui batasan waktu dan demografi."
        )
    )

# ── WALL-E (2008) ──────────────────────────────────────────────

def analyze_walle_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "looney_tune" in w and ("sound_effect" in w or "never_let" in w):
        return (
            "Narasi Tanpa Dialog dan Ekspresi Visual",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap kemampuan WALL-E bercerita secara efektif selama lebih dari setengah jam pertama tanpa dialog, mengandalkan ekspresi visual, gestur, dan efek suara. Kemampuan ini dinilai sebagai pencapaian sinematik yang luar biasa.",
                f"'Looney_tune', 'sound_effect', 'never_let', 'human_being', dan 'andrew_stanton' menunjukkan apresiasi terhadap tradisi slapstick visual yang direnovasi untuk konteks modern. Referensi ke Looney Tunes mengindikasikan warisan komedi visual. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar apresiasi terhadap pendekatan narasi tanpa dialog sebagai kekuatan utama.",
                "WALL-E mendemonstrasikan bahwa narasi visual tanpa dialog mampu membangun koneksi emosional yang lebih mendalam dari dialog eksplisit, merevitalisasi tradisi film bisu dalam konteks animasi modern."
            )
        )
    if "plant_life" in w and ("waste_allocation" in w or "space_ship" in w):
        return (
            "Bumi Pasca-Apokaliptik dan Simbol Harapan",
            build_notes(
                "Topik ini merepresentasikan respons penonton terhadap world-building WALL-E — bumi yang dipenuhi sampah dan ditinggalkan manusia — sebagai latar dystopia yang berfungsi sekaligus sebagai kritik lingkungan dan konteks emosional untuk kisah cinta protagonis.",
                f"'Plant_life', 'waste_allocation', 'space_ship', 'load_lifter', dan 'robot_clean' menunjukkan perhatian terhadap detail world-building. Satu tanaman sebagai simbol harapan menjadi motif narasi yang berulang. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar dimensi world-building dan kritik lingkungan mendominasi diskusi.",
                "Bumi yang dipenuhi sampah dalam WALL-E berfungsi sebagai kritik lingkungan yang viseral sekaligus latar emosional yang memperkuat kerinduan WALL-E sebagai satu-satunya penjaga dunia yang ditinggalkan."
            )
        )
    if "no_dialogue" in w or ("child_adult" in w and "human_being" in w):
        return (
            "Kisah Cinta Robot Lintas Generasi",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap kisah cinta WALL-E dan EVE sebagai narasi yang berhasil menciptakan resonansi emosional mendalam tanpa mengandalkan dialog verbal. Film ini membuktikan bahwa empati tidak memerlukan kata-kata.",
                f"'No_dialogue', 'child_adult', 'human_being', 'quality_animation', dan 'andrew_stanton' menunjukkan koneksi antara keterbatasan bahasa verbal dengan pencapaian komunikasi emosional. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan bahwa kisah cinta robot ini beresonansi secara signifikan dalam evaluasi penonton.",
                "Kisah cinta antara WALL-E dan EVE membuktikan bahwa empati dan koneksi emosional yang mendalam dapat dibangun tanpa satu kata dialog pun."
            )
        )
    if "space_odyssey" in w and ("care_planet" in w or "sight_gag" in w):
        return (
            "Referensi Kubrick dan Kritik Konsumerisme",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton yang menangkap lapisan intelektual WALL-E — referensi ke 2001: A Space Odyssey dan kritik terhadap konsumerisme berlebihan — sebagai dimensi yang mengangkat film melampaui kategori animasi keluarga.",
                f"'Space_odyssey', 'care_planet', 'important_message', dan 'sight_gag' menunjukkan kemampuan penonton mendeteksi intertekstualitas dan dimensi tematik. Referensi Kubrick mengindikasikan ambisi sinematik yang disengaja. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan penonton yang mampu membaca film pada level intertekstual.",
                "WALL-E berhasil mengintegrasikan referensi sinematik ke 2001: A Space Odyssey dengan kritik konsumerisme yang relevan, menempatkan film ini di antara karya sains fiksi yang paling substantif secara intelektual."
            )
        )
    if "science_fiction" in w and ("andrew_stanton" in w or "space_odyssey" in w):
        return (
            "WALL-E sebagai Sains Fiksi Dewasa",
            build_notes(
                "Topik ini merepresentasikan penilaian penonton yang menempatkan WALL-E bukan hanya sebagai film animasi keluarga, tetapi sebagai sains fiksi yang substantif dengan visi yang sebanding dengan karya-karya terbaik genre tersebut.",
                f"'Science_fiction', 'andrew_stanton', 'space_odyssey', dan 'quality_animation' menunjukkan klaim tentang posisi film dalam kanon sains fiksi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menempatkan film dalam konteks genre sains fiksi yang lebih luas.",
                "WALL-E dinilai melampaui batasan film animasi keluarga dan berhasil mengambil posisi di antara karya sains fiksi paling substantif dan visioner dalam sejarah sinema."
            )
        )
    if "important_message" in w and ("body_language" in w or "load_lifter" in w):
        return (
            "Pesan Lingkungan melalui Bahasa Tubuh",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap cara WALL-E menyampaikan pesan lingkungan melalui bahasa non-verbal — bukan ceramah atau dialog eksplisit, melainkan melalui gambaran visual yang berbicara sendiri.",
                f"'Important_message', 'body_language', 'load_lifter', dan 'waste_allocation' menunjukkan identifikasi terhadap strategi komunikasi tematik yang non-didaktis. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar pesan lingkungan diidentifikasi sebagai komponen tematik yang signifikan.",
                "WALL-E menyampaikan pesan lingkungan yang mendesak melalui bahasa visual yang non-didaktis, membuktikan bahwa kritik sosial yang efektif tidak memerlukan eksposisi eksplisit."
            )
        )
    if "robot_clean" in w or "short_circuit" in w:
        return (
            "Robot-Robot Sisa dan Ekosistem Dunia WALL-E",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap detail world-building WALL-E yang meluas melampaui protagonis — robot-robot lain yang sudah berhenti berfungsi memberikan konteks tentang dunia yang telah lama ditinggalkan.",
                f"'Robot_clean', 'short_circuit', 'space_axiom', 'load_lifter', dan 'body_language' menunjukkan perhatian terhadap detail ekosistem dunia fiksi. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menghargai detail world-building di luar narasi utama.",
                "Kehadiran robot-robot lain yang telah berhenti berfungsi memberikan konteks yang memperkaya world-building WALL-E, membangun narasi implied tentang dunia yang telah lama dikosongkan manusia."
            )
        )
    return (
        "Ekspresi Emosi dan Romansa Tanpa Kata",
        build_notes(
            "Topik ini merepresentasikan penilaian umum tentang kemampuan WALL-E membangun narasi emosional yang kuat tanpa ketergantungan pada dialog verbal.",
            f"Kombinasi kata-kata tentang interaksi robot dan emosi menunjukkan evaluasi terhadap kemampuan bercerita non-verbal. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penilaian yang berfokus pada dimensi emosional.",
            "WALL-E menghadirkan narasi emosional yang kuat melalui bahasa non-verbal, membuktikan kemampuan ekspresi visual sebagai medium komunikasi yang lebih universal dari dialog."
        )
    )

def analyze_walle_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "heart" in w and ("relationship" in w or "care" in w):
        return (
            "Kisah Cinta yang Mengharukan",
            build_notes(
                "Topik ini merepresentasikan respons emosional penonton terhadap kisah cinta WALL-E dan EVE — sebuah romansa yang berhasil membuat penonton berinvestasi secara emosional pada dua entitas non-manusia. Ini merupakan pencapaian empati yang luar biasa.",
                f"'Heart', 'relationship', 'robot', 'care', dan 'human' menunjukkan respons afektif yang mengidentifikasi kisah cinta sebagai inti emosional film. Kontras 'robot' dengan 'heart' mengindikasikan paradoks yang menjadi kekuatan film. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar kisah cinta mendominasi sebagai aspek emosional yang paling berkesan.",
                "Kisah cinta WALL-E dan EVE berhasil menciptakan empati yang mendalam terhadap entitas non-manusia, membuktikan bahwa koneksi emosional bersifat universal melampaui batas medium."
            )
        )
    if "message" in w and ("not_be" in w or "robot" in w) and "kid" not in w:
        return (
            "Robot sebagai Metafora Harapan",
            build_notes(
                "Topik ini merepresentasikan penilaian penonton yang melihat WALL-E bukan hanya sebagai karakter fiksi, melainkan sebagai metafora tentang ketaatan dan harapan di tengah dunia yang telah menyerah. Film ini menggunakan robot sebagai medium untuk menyampaikan pesan tentang tanggung jawab.",
                f"'Animation', 'robot', 'message', 'human', dan 'not_be' menunjukkan analisis tematik yang mengidentifikasi robot sebagai wahana pesan moral. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang membaca film pada level tematik.",
                "WALL-E berfungsi sebagai metafora tentang ketaatan dan harapan — satu-satunya entitas yang masih menjalankan tugasnya di dunia yang telah meninggalkan tanggung jawab."
            )
        )
    if "no_dialogue" in w or ("expression" in w and "body" in w):
        return (
            "Bahasa Visual sebagai Narasi Utama",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap kemampuan WALL-E membawa tradisi film bisu ke konteks animasi modern — di mana ekspresi tubuh dan sound design menggantikan dialog sebagai medium utama penceritaan.",
                f"'No_dialogue', 'expression', 'body', 'movement', dan 'animation' menunjukkan identifikasi terhadap strategi narasi visual yang dominan. Konteks tradisi film bisu Chaplin dan Keaton relevan. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distributi {dist_pct:.1f}%, topik ini menunjukkan penonton yang mengidentifikasi bahasa visual sebagai inovasi naratif terbesar film.",
                "WALL-E merevitalisasi tradisi film bisu dalam konteks animasi kontemporer, membuktikan supremasi bahasa visual sebagai medium naratif yang paling murni dan universal."
            )
        )
    if "family" in w or "environment" in w:
        return (
            "Pesan Lingkungan dalam Kemasan Keluarga",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap keberanian Pixar menyampaikan pesan lingkungan yang serius melalui medium film keluarga — sebuah keputusan yang memungkinkan pesan tersebut menjangkau audiens yang jauh lebih luas.",
                f"'Family', 'environment', 'life', 'short', dan 'message' menunjukkan identifikasi terhadap strategi misi pesan melalui medium yang akrab. Konteks Pixar sebagai studio keluarga memperkuat ironisnya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi pesan lingkungan sebagai tema utama.",
                "WALL-E berhasil mengemas pesan lingkungan yang krusial dalam format film keluarga, memaksimalkan jangkauan pesan melalui medium yang memiliki audiens paling luas."
            )
        )
    if "space" in w and ("ship" in w or "waste" in w):
        return (
            "Axiom dan Kritik Konsumerisme Manusia",
            build_notes(
                "Topik ini merepresentasikan respons penonton terhadap gambaran manusia masa depan di atas kapal Axiom — sebagai satir terhadap konsumerisme, obesitas, dan ketergantungan teknologi yang terasa semakin relevan setiap tahunnya.",
                f"'Space', 'ship', 'human', 'waste', dan 'not_in' menunjukkan respons terhadap bagian kedua film yang lebih eksplisit dalam kritik sosialnya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar satir sosial tentang konsumerisme menjadi topik diskusi.",
                "Gambaran manusia di atas kapal Axiom merupakan satir yang tajam tentang konsumerisme dan ketergantungan teknologi yang relevansinya terus meningkat setiap tahun."
            )
        )
    if "no_one" in w or ("beautiful" in w and "stanton" in w):
        return (
            "Keindahan Kesepian dan Visi Artistik Stanton",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap estetika kesepian WALL-E — gambaran-gambaran indah tentang satu robot yang sendirian di antara reruntuhan peradaban — yang menjadi salah satu momen visual paling berkesan dalam sinema animasi.",
                f"'No_one', 'beautiful', 'human', 'stanton', dan 'no_doubt' menunjukkan identifikasi terhadap estetika kesendirian sebagai pilihan artistik yang disengaja. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi estetika visual sebagai komponen penilaian utama.",
                "Estetika kesendirian WALL-E — gambaran indah tentang satu makhluk di antara reruntuhan peradaban — menjadi identitas visual film yang paling khas dan paling berkesan."
            )
        )
    if "message" in w and ("kid" in w or "computer" in w):
        return (
            "Relevansi Pesan bagi Generasi Digital",
            build_notes(
                "Topik ini merepresentasikan relevansi pesan WALL-E bagi penonton dari generasi yang tumbuh dalam era digital — di mana ketergantungan pada layar dan mesin menjadi kenyataan yang semakin dekat dengan gambaran dystopia yang disajikan film.",
                f"'Message', 'kid', 'computer', 'human', 'graphic', dan 'planet' menunjukkan diskursus tentang relevansi kontemporer pesan film. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan penonton yang mengidentifikasi relevansi pesan dalam konteks kehidupan mereka sendiri.",
                "Pesan WALL-E tentang konsumerisme dan ketergantungan teknologi memiliki resonansi yang semakin kuat bagi generasi digital yang kenyataan hidupnya semakin menyerupai dystopia yang digambarkan film."
            )
        )
    if "robot" in w and ("garbage" in w or "stanton" in w):
        return (
            "WALL-E sebagai Pekerja Terakhir yang Setia",
            build_notes(
                "Topik ini merepresentasikan interpretasi penonton terhadap WALL-E sebagai figur yang tragis sekaligus heroik — satu-satunya entitas yang masih menjalankan tugasnya dengan setia dalam dunia yang sudah lama meninggalkan tanggung jawab.",
                f"'Robot', 'garbage', 'stanton', dan 'human' menunjukkan identifikasi terhadap dimensi tragis karakter yang bekerja tanpa pengakuan selama berabad-abad. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menginterpretasikan karakter pada level tematik.",
                "WALL-E sebagai satu-satunya robot yang masih berfungsi mewakili sebuah tragedi implisit — ketaatan pada tugas di dunia yang telah melupakan tanggung jawab — yang menjadi subtext emosional paling kuat film."
            )
        )
    return (
        "Emosi dan Pesan dalam Animasi Pixar",
        build_notes(
            "Topik ini merepresentasikan penilaian umum terhadap WALL-E sebagai pencapaian Pixar dalam mengintegrasikan emosi mendalam dengan pesan bermakna dalam format animasi.",
            f"Kombinasi kata-kata tentang manusia, animasi, dan pesan menunjukkan evaluasi holistik. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penilaian yang bersifat menyeluruh.",
            "WALL-E merepresentasikan puncak kemampuan Pixar dalam mengintegrasikan dimensi emosional yang mendalam dengan pesan tematik yang bermakna dalam format animasi."
        )
    )

# ── YOUR NAME (2016) ───────────────────────────────────────────

def analyze_yourname_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "start_finish" in w and ("studio_ghibli" in w or "sound_design" in w):
        return (
            "Pengalaman Menonton yang Mendebarkan",
            build_notes(
                "Topik ini merepresentasikan penilaian penonton terhadap Your Name sebagai film yang berhasil mempertahankan ketegangan dan minat dari awal hingga akhir tanpa memberi kesempatan bernapas. Tempo penceritaan yang terukur dan akhir yang emosional menjadi komponen utama.",
                f"'Start_finish', 'studio_ghibli', 'high_expectation', 'sound_design', dan 'switch_body' menunjukkan penilaian pengalaman menonton secara menyeluruh. Referensi Ghibli mengindikasikan standar perbandingan. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menilai kualitas pengalaman menonton secara holistik.",
                "Your Name berhasil mempertahankan keterlibatan penonton dari awal hingga akhir melalui tempo penceritaan yang terukur dan akhir yang memukul secara emosional."
            )
        )
    if "not_great" in w and ("no_na" in w or "japanese_culture" in w):
        return (
            "Evaluasi Kritis: Antara Hype dan Substansi",
            build_notes(
                "Topik ini merepresentasikan pandangan penonton yang mengevaluasi Your Name dengan perspektif lebih kritis terhadap kesenjangan antara reputasinya dan kualitas naratif yang sesungguhnya. Ulasan ini tidak menolak film, namun menyertakan reservasi.",
                f"'Not_great', 'no_na', 'japanese_culture', 'fantastic_soundtrack', dan 'never_thought' menunjukkan pola penilaian yang memisahkan antara aspek yang berhasil (musik, visual) dan yang kurang (narasi). Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang memberikan penilaian bernuansa dan kritis.",
                "Sebagian penonton mengevaluasi Your Name dengan memisahkan keunggulan visual dan musikal dari aspek naratif yang dianggap tidak selalu sepadan dengan reputasinya."
            )
        )
    if "high_school" in w and ("small_town" in w or "hayao_miyazaki" in w):
        return (
            "Estetika Kehidupan Jepang: Kota dan Desa",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap kontras visual dan kultural antara kehidupan kota Tokyo dan desa Itomori yang menjadi dua latar utama Your Name. Detail kehidupan Jepang yang autentik menjadi sumber apresiasi tersendiri.",
                f"'High_school', 'small_town', 'hayao_miyazaki', 'animation_beautiful', dan 'attention_detail' menunjukkan fokus pada representasi kehidupan Jepang yang terperinci. Referensi Miyazaki menunjukkan standar komparatif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar representasi kehidupan Jepang berkontribusi dalam evaluasi penonton.",
                "Kontras antara kehidupan urban Tokyo dan kehidupan desa Itomori dihadirkan dengan ketelitian detail yang membuat penonton internasional merasakan keautentikan budaya Jepang."
            )
        )
    if "beautiful_animation" in w and ("life_live" in w or "music_choice" in w or "romantic_comedy" in w):
        return (
            "Animasi yang Memukau dan Romansa yang Memikat",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap kualitas visual Your Name yang menjadi salah satu benchmark animasi kontemporer, dikombinasikan dengan daya tarik romansa yang menjadi daya pikat utama narasi.",
                f"'Beautiful_animation', 'life_live', 'music_choice', 'romantic_comedy', dan 'never_seen' menunjukkan integrasi antara apresiasi visual dan afeksi terhadap narasi romantis. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar kombinasi visual dan romansa mendominasi dalam penilaian.",
                "Kualitas animasi Your Name yang memukau berfungsi sebagai bingkai sempurna bagi narasi romantis yang berhasil membuat penonton berinvestasi emosional pada kisah dua karakter."
            )
        )
    if "romantic_comedy" in w and ("switch_body" in w or "no_na" in w):
        return (
            "Komedi Segar dari Mekanisme Body Swap",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap aspek komedi Your Name yang sering diabaikan — humor yang lahir dari kebingungan dan canggungnya situasi body swap antara Makoto dan Mitsuha. Humor ini menyeimbangkan dimensi melankolis narasi.",
                f"'Romantic_comedy', 'switch_body', 'no_na', 'never_seen', dan 'without_even' menunjukkan identifikasi terhadap komponen komedi sebagai penyeimbang tonal. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi elemen komedi sebagai kekuatan tonal yang signifikan.",
                "Humor yang lahir dari situasi body swap berfungsi sebagai penyeimbang tonal yang efektif, memberikan ruang napas sebelum narasi Your Name memasuki dimensi yang lebih berat dan emosional."
            )
        )
    if "sound_design" in w or "human_emotion" in w:
        return (
            "Desain Suara dan Resonansi Emosional",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap cara RADWIMPS mengintegrasikan musik bukan sebagai pelengkap visual, melainkan sebagai perpanjangan emosi karakter yang membawa penonton ke dalam pengalaman subjektif yang lebih mendalam.",
                f"'Sound_design', 'human_emotion', 'garden_word', dan 'style_substance' menunjukkan identifikasi terhadap musik sebagai komponen naratif yang fungsional, bukan dekoratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar dimensi audio berkontribusi dalam membentuk pengalaman emosional.",
                "Musik RADWIMPS dalam Your Name berfungsi sebagai ekspresi langsung dari emosi karakter, menciptakan layer pengalaman yang melampaui apa yang bisa disampaikan melalui visual atau dialog saja."
            )
        )
    if "fate_connection" in w or ("music_choice" in w and "attention_detail" in w):
        return (
            "Takdir, Koneksi, dan Keyakinan Spiritual",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap tema takdir dan koneksi lintas waktu yang menjadi fondasi mitologi Your Name. Konsep 'musubi' — koneksi yang tertulis dalam alam semesta — dipandang sebagai premis naratif yang unik dan bermakna.",
                f"'Fate_connection', 'beautiful_animation', 'music_choice', 'hayao_miyazaki', dan 'attention_detail' menunjukkan identifikasi terhadap dimensi spiritual dan mitologis. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar tema takdir berkontribusi dalam penilaian penonton.",
                "Tema takdir dan koneksi yang melampaui waktu dalam Your Name, bersumber dari konsep 'musubi' dalam tradisi Shinto, memberikan fondasi mitologis yang memperkuat resonansi emosional narasi."
            )
        )
    if "not_good" in w and ("japanese_culture" in w or "hayao_miyazaki" in w):
        return (
            "Kritik Narasi dalam Konteks Budaya Jepang",
            build_notes(
                "Topik ini merepresentasikan pandangan penonton yang mengapresiasi representasi budaya Jepang namun menemukan kelemahan dalam aspek naratif tertentu. Evaluasi ini cenderung lebih analitis dan kontekstual.",
                f"'Not_good', 'japanese_culture', 'hayao_miyazaki', 'small_town', dan 'life_live' menunjukkan penilaian yang memisahkan kualitas representasi budaya dari kualitas naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang menyertakan reservasi kritis dalam evaluasi.",
                "Sebagian penonton mengakui keindahan representasi budaya Jepang dalam Your Name sambil mengidentifikasi kelemahan naratif yang dianggap mengurangi potensi maksimalnya."
            )
        )
    if "never_seen" in w and ("animation_beautiful" in w or "no_na" in w):
        return (
            "Pengalaman Visual yang Benar-Benar Baru",
            build_notes(
                "Topik ini merepresentasikan respons penonton yang baru pertama kali terekspos pada gaya animasi Makoto Shinkai — sebuah estetika yang menggabungkan realisme fotografis dengan keindahan imajinatif yang menghasilkan sesuatu yang belum pernah mereka lihat sebelumnya.",
                f"'Never_seen', 'animation_beautiful', 'no_na', dan 'original_japanese' menunjukkan pengalaman pertama yang meninggalkan kesan mendalam. Konteks 'anime pertama' bagi sebagian penonton relevan. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar faktor kebaruan pengalaman visual membentuk respons positif.",
                "Your Name memperkenalkan estetika visual Makoto Shinkai kepada penonton internasional sebagai pengalaman yang belum pernah ada sebelumnya, membuka pintu apresiasi terhadap animasi Jepang."
            )
        )
    return (
        "Animasi Indah dan Narasi Romantis",
        build_notes(
            "Topik ini merepresentasikan penilaian umum penonton terhadap Your Name sebagai film animasi yang berhasil memadukan kecantikan visual dengan narasi romantis yang memikat.",
            f"Kombinasi kata-kata tentang animasi, musik, dan romansa menunjukkan evaluasi holistik. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penilaian yang bersifat komprehensif.",
            "Your Name berhasil memadukan keindahan visual animasi Shinkai dengan narasi romantis yang emosional, menjadikannya salah satu film animasi Jepang yang paling diakui secara global."
        )
    )

def analyze_yourname_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "makoto" in w and ("protagonist" in w or "journey" in w):
        return (
            "Makoto sebagai Protagonis yang Mudah Dicintai",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap kepribadian dan arc karakter Makoto Shinkai sebagai salah satu protagonis animasi yang paling mudah diidentifikasi. Keterbatasan dan pertumbuhannya resonan secara universal.",
                f"'Animation', 'makoto', 'protagonist', 'journey', dan 'emotion' menunjukkan fokus pada pengembangan karakter sebagai kekuatan naratif. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi karakter sebagai komponen utama pengalaman.",
                "Makoto Shinkai sebagai protagonis berhasil menghadirkan sosok yang mudah diidentifikasi dan dicintai, menjadikan perjalanan emosionalnya sebagai pengalaman yang terasa personal bagi penonton."
            )
        )
    if "style" in w and ("fantasy" in w or "school" in w or "high" in w):
        return (
            "Gaya Visual Dreamlike yang Khas Shinkai",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap identitas visual Makoto Shinkai yang khas — cara khusus merender cahaya, air, dan langit yang menciptakan estetika dreamlike yang menjadi tanda tangan artistiknya.",
                f"'Animation', 'style', 'fantasy', 'japanese', dan 'beautiful' menunjukkan identifikasi terhadap estetika visual yang konsisten dan identifiable. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini menunjukkan seberapa besar gaya visual Shinkai menjadi komponen apresiasi yang eksplisit.",
                "Estetika visual Makoto Shinkai yang khas — terutama dalam pengolahan cahaya, partikel, dan langit — membentuk identitas visual Your Name yang mudah dikenali dan menjadi benchmark kualitas animasi kontemporer."
            )
        )
    if "ghibli" in w or "studio" in w or "voice" in w:
        return (
            "Warisan Ghibli dan Posisi Shinkai dalam Animasi Jepang",
            build_notes(
                "Topik ini merepresentasikan diskusi tentang posisi Makoto Shinkai dalam lanskap animasi Jepang dan hubungannya dengan warisan Studio Ghibli. Perbandingan dan perbedaan antara dua pendekatan artistik menjadi topik diskusi.",
                f"'Music', 'ghibli', 'studio', 'voice', dan 'theme' menunjukkan diskursus tentang konteks industri dan lineage artistik. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mendekati film dalam konteks tradisi animasi Jepang.",
                "Your Name menduduki posisinya sendiri dalam lanskap animasi Jepang — tidak hanya sebagai penerus Ghibli, tetapi sebagai pendefinisi estetika baru yang mencerminkan sensibilitas generasi kontemporer."
            )
        )
    if "no_na" in w and ("perfect" in w or "taste" in w):
        return (
            "Konteks Budaya dan Aksesibilitas untuk Penonton Global",
            build_notes(
                "Topik ini merepresentasikan diskusi tentang bagaimana konteks budaya Jepang mempengaruhi aksesibilitas dan kedalaman apresiasi penonton internasional. Elemen seperti tradisi 'musubi' menambahkan lapisan makna yang membutuhkan pemahaman kontekstual.",
                f"'No_na', 'perfect', 'japanese', 'not_to', dan 'taste' menunjukkan negosiasi antara pengalaman universal film dan lapisan kultural yang spesifik. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi aspek kultural sebagai bagian dari pengalaman.",
                "Your Name berhasil menjangkau penonton global meskipun mengandung elemen budaya Jepang yang spesifik, membuktikan bahwa universalitas emosi melampaui batas-batas konteks budaya."
            )
        )
    if "not_good" in w and ("tokyo" in w or "live" in w):
        return (
            "Kehidupan Urban Tokyo dan Dimensi Sosial",
            build_notes(
                "Topik ini merepresentasikan apresiasi atau kritik terhadap representasi kehidupan urban Tokyo yang menjadi salah satu dari dua latar utama film. Dinamika antara kehidupan kota modern dan kampung halaman tradisional mengandung subtext tentang modernitas dan identitas.",
                f"'Not_good', 'live', 'tokyo', 'japanese', dan 'beautiful' menunjukkan diskursus tentang representasi kehidupan urban Jepang. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mendekati film dari perspektif representasi sosial.",
                "Representasi kehidupan urban Tokyo dalam Your Name mengandung dimensi sosial tentang keterasingan modernitas yang menjadi kontras produktif dengan keakraban kehidupan desa Itomori."
            )
        )
    if "makoto" in w and ("not_great" in w or "no_na" in w or "hype" in w):
        return (
            "Twist Naratif dan Evaluasi Struktural",
            build_notes(
                "Topik ini merepresentasikan diskusi penonton tentang twist naratif utama Your Name dan seberapa efektif strukturnya dalam mendukung resolusi emosional. Penilaian ini cenderung lebih analitis secara naratif.",
                f"'Animation', 'makoto', 'not_great', 'no_na', dan 'hype' menunjukkan evaluasi struktural yang lebih kritis. Konteks hype sebagai standar perbandingan memengaruhi penilaian. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengevaluasi film dari perspektif struktural naratif.",
                "Twist naratif utama Your Name mengundang evaluasi yang beragam — dari mereka yang menganggapnya sebagai keputusan jenius hingga yang merasa pacing resolusinya bisa lebih optimal."
            )
        )
    if "connection" in w or ("magic" in w and ("emotional" in w or "distance" in w)):
        return (
            "Koneksi Takdir yang Melampaui Waktu",
            build_notes(
                "Topik ini merepresentasikan apresiasi terhadap tema paling universal Your Name — keyakinan bahwa beberapa koneksi manusiawi begitu kuat sehingga melampaui batas yang tampak tidak mungkin. Tema ini beresonansi karena menyentuh kerinduan universal tentang koneksi.",
                f"'Connection', 'magic', 'emotional', 'distance', dan 'never_thought' menunjukkan respons emosional terhadap tema koneksi dan takdir. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan seberapa besar tema koneksi lintas waktu beresonansi dalam diskusi penonton.",
                "Tema koneksi yang melampaui waktu dan jarak dalam Your Name beresonansi secara universal karena menyentuh kerinduan manusiawi yang paling fundamental tentang terhubung dengan orang lain."
            )
        )
    if "powerful" in w or ("beautiful" in w and "sound" in w):
        return (
            "Dampak Emosional yang Kuat dan Menyeluruh",
            build_notes(
                "Topik ini merepresentasikan penilaian tentang dampak emosional keseluruhan Your Name — bagaimana film berhasil menciptakan pengalaman afektif yang intens tanpa penonton menyadari kapan persisnya film tersebut berhasil masuk ke dalam hati mereka.",
                f"'Powerful', 'beautiful', 'sound', 'animation', dan 'without_even' menunjukkan respons afektif yang dialami tanpa diduga. Ketidaksengajaan ini menjadi penanda dampak yang paling kuat. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang melaporkan dampak emosional sebagai pengalaman dominan.",
                "Your Name menciptakan dampak emosional yang intens secara bertahap tanpa disadari penonton, membuktikan keahlian Shinkai dalam membangun keterlibatan emosional yang organis."
            )
        )
    if "girl" in w and ("no_na" in w or "not_as" in w):
        return (
            "Identitas dan Pengalaman Subjektif Karakter",
            build_notes(
                "Topik ini merepresentasikan diskusi tentang dimensi identitas dalam Your Name — bagaimana Makoto dan Mitsuha mengalami perspektif satu sama lain sebagai bentuk eksplorasi tentang diri dan identitas yang lebih luas.",
                f"'Girl', 'no_na', 'not_as', 'animation', dan 'beautiful' menunjukkan diskursus tentang pengalaman subjektif dan identitas gender dalam konteks body swap. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penonton yang mengidentifikasi tema identitas sebagai dimensi yang bermakna.",
                "Mekanisme body swap dalam Your Name berfungsi sebagai eksplorasi tentang identitas dan perspektif — bagaimana pengalaman melihat dunia melalui mata orang lain mengubah pemahaman tentang diri sendiri."
            )
        )
    return (
        "Animasi dan Emosi yang Berpadu",
        build_notes(
            "Topik ini merepresentasikan penilaian umum terhadap Your Name sebagai film yang berhasil memadukan keindahan animasi dengan kedalaman emosional.",
            f"Kombinasi kata-kata tentang animasi, keindahan, dan emosi menunjukkan evaluasi holistik. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menunjukkan proporsi penilaian yang bersifat komprehensif.",
            "Your Name berhasil menjadi tolok ukur baru dalam animasi Jepang dengan memadukan keindahan visual yang memukau dan kedalaman emosional yang beresonansi secara universal."
        )
    )

# ================================================================
# FUNGSI DISPATCH UTAMA
# ================================================================

FILM_DISPATCHERS = {
    "Avengers_Endgame_2019": {"bigram": analyze_avengers_bigram, "unigram": analyze_avengers_unigram},
    "Coco_2017":              {"bigram": analyze_coco_bigram,      "unigram": analyze_coco_unigram},
    "Interstellar_2014":      {"bigram": analyze_interstellar_bigram, "unigram": analyze_interstellar_unigram},
    "Parasite_2019":          {"bigram": analyze_parasite_bigram,  "unigram": analyze_parasite_unigram},
    "Spider_Man_Into_The_Spider_Verse_2018": {"bigram": analyze_spiderverse_bigram, "unigram": analyze_spiderverse_unigram},
    "The_Dark_Knight_2008":   {"bigram": analyze_tdk_bigram,       "unigram": analyze_tdk_unigram},
    "The_Lord_Of_The_Rings_The_Return_Of_The_King_2003": {"bigram": analyze_lotr_bigram, "unigram": analyze_lotr_unigram},
    "Toy_Story_1995":         {"bigram": analyze_toystory_bigram,  "unigram": analyze_toystory_unigram},
    "WALL_E_2008":            {"bigram": analyze_walle_bigram,     "unigram": analyze_walle_unigram},
    "Your_Name_2016":         {"bigram": analyze_yourname_bigram,  "unigram": analyze_yourname_unigram},
}

# ================================================================
# EKSEKUSI UTAMA
# ================================================================

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('SELECT id_title, result_data FROM movie_analysis')
rows = cur.fetchall()
conn.close()

db_map = {}
for r in rows:
    try:
        db_map[r['id_title']] = json.loads(r['result_data'])
    except:
        pass

total_ok = 0
total_fail = 0

for db_key, data in db_map.items():
    m = re.match(r'^(.+)_(unigram|bigram)_k(\d+)$', db_key)
    if not m:
        continue

    film_key = m.group(1)
    mode     = m.group(2)
    k        = int(m.group(3))

    if film_key not in FILM_DISPATCHERS:
        continue

    dispatcher = FILM_DISPATCHERS[film_key][mode]
    topics     = data.get('topics', {})
    title_from_data = data.get('title', film_key)

    # Hitung total distribusi untuk persentase
    total_dist = 0
    for tdata in topics.values():
        words = tdata.get('words', [])
        total_dist += sum(w['weight'] for w in words) if words else 1

    print(f"\n[{db_key}]")

    topic_list = list(topics.items())
    for tidx, (topic_name, topic_data) in enumerate(topic_list):
        words      = [w['word'] for w in topic_data.get('words', [])[:15]]
        contoh     = topic_data.get('contoh_ulasan', ['(tidak tersedia)'])
        if not contoh:
            contoh = ['(tidak tersedia)']

        # Hitung distribusi topik ini
        topic_weights = [w['weight'] for w in topic_data.get('words', [])]
        topic_sum = sum(topic_weights) if topic_weights else 0
        dist_pct = (topic_sum / max(total_dist, 0.001)) * 100 if total_dist > 0 else (100.0 / max(len(topics), 1))

        if not words:
            continue

        label, notes = dispatcher(words, contoh, dist_pct, tidx, len(topic_list))
        label = clean_label(label)

        payload = {
            "title":        title_from_data,
            "num_topics":   k,
            "mode":         mode,
            "topic_id":     topic_name,
            "custom_label": label,
            "notes":        notes,
        }

        try:
            res = requests.post(f"{API_BASE}/update_interpretation", json=payload, timeout=15)
            result = res.json()
            if result.get("status") == "success":
                print(f"  [OK] {topic_name}: {label}")
                total_ok += 1
            else:
                print(f"  [FAIL] {topic_name}: {result.get('error')}")
                total_fail += 1
        except Exception as e:
            print(f"  [ERR] {topic_name}: {e}")
            total_fail += 1

print(f"\n{'='*60}")
print(f"SELESAI: {total_ok} berhasil, {total_fail} gagal.")

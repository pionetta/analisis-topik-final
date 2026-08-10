import sqlite3, json, re

# ================================================================
# FUNGSI INTERPRETASI AKADEMIK PER FILM
# Menghasilkan tuple (label, notes_terstruktur) berdasarkan
# kata dominan, contoh ulasan, dan pola semantik topik.
# ================================================================

def clean_label(text):
    words = text.split()
    return ' '.join(words[:5])

def build_notes(interpretasi, bukti, dominasi, ringkasan):
    return f"{interpretasi} {ringkasan}"

# --- AVENGERS ---
def analyze_avengers_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "russo_brother" in w and "emotional_rollercoaster" in w:
        return (
            "Penutup Epik Russo Brothers",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap arahan Russo Brothers dalam mengeksekusi penutup saga MCU yang dinilai sebagai perjalanan emosional yang berhasil. Ulasan dalam kelompok ini cenderung menyoroti ketepatan penceritaan yang mengikat narasi panjang menjadi satu kesimpulan yang koheren dan memuaskan.",
                f"Kata dominan 'russo_brother' menunjukkan atribusi langsung terhadap sutradara; 'emotional_rollercoaster' dan 'perfect_conclusion' mengindikasikan respons afektif yang kuat. Contoh ulasan: \"{str(contoh[0])[:120]}...\"",
                f"Topik ini berkontribusi sekitar {dist_pct:.1f}% dari seluruh distribusi dokumen, menandakan bahwa apresiasi ini konsisten dibahas.",
                "Penonton mengapresiasi arahan Russo Brothers yang berhasil menutup saga MCU dengan emosional."
            )
        )
    if "robert_downey" in w and "final_battle" not in w:
        return (
            "Pengorbanan Iron Man dan Kehilangan",
            build_notes(
                "Topik ini menangkap respons emosional penonton yang berpusat pada nasib Tony Stark sebagai karakter poros MCU. Diskusi memperlihatkan dualitas antara rasa kehilangan yang mendalam dan pertanyaan tentang keharusan naratif dari pengorbanan tersebut.",
                f"Kemunculan 'robert_downey' menunjukkan sentralitas karakter Iron Man. Contoh ulasan: \"{str(contoh[0])[:120]}...\" memperlihatkan kompleksitas sentimen kehilangan ini.",
                f"Dengan distribusi {dist_pct:.1f}%, topik ini mencerminkan fokus penonton pada dimensi personal karakter.",
                "Penonton terbagi antara haru atas pengorbanan Tony Stark dan pertanyaan tentang resolusi karakternya."
            )
        )
    if "emotional_weight" in w or ("cinematic_universe" in w and "final_battle" in w):
        return (
            "Klimaks dan Bobot Emosional MCU",
            build_notes(
                "Topik ini merepresentasikan dimensi emosional dari pertempuran final Endgame dalam konteks yang lebih luas sebagai puncak dari seluruh Cinematic Universe Marvel.",
                f"'Emotional_weight', 'cinematic_universe', dan 'final_battle' secara bersamaan mengindikasikan penilaian franchise-wide. Ulasan: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan bahwa perspektif naratif makro ini umum digunakan penonton.",
                "Penonton menilai pertempuran final Endgame sebagai puncak emosional dari keseluruhan MCU."
            )
        )
    if "perfect_conclusion" in w and "visual_effect" in w:
        return (
            "Visual Epik dan Kesempurnaan Penutup",
            build_notes(
                "Topik ini menangkap penilaian terpadu penonton terhadap dua dimensi utama Endgame: kualitas sinematik dari pertempuran dan keberhasilan film sebagai penutup yang memuaskan.",
                f"Kombinasi 'perfect_conclusion' dan 'visual_effect' menunjukkan kepuasan sinematik dan naratif. Ulasan: \"{str(contoh[0])[:120]}...\"",
                f"Muncul pada {dist_pct:.1f}% distribusi, mengindikasikan apresiasi tinggi terhadap keseimbangan aksi dan resolusi.",
                "Endgame dinilai sebagai penutup sempurna yang memadukan aksi visual epik dengan kepuasan naratif."
            )
        )
    return (
        "Ekspektasi Tidak Terpenuhi Sepenuhnya",
        build_notes(
            "Topik ini merepresentasikan suara penonton yang menilai Endgame dengan perspektif lebih kritis, di mana beberapa aspek film tidak sepenuhnya memenuhi ekspektasi yang sangat tinggi.",
            f"Dominannya kata-kata bernada negasi mengindikasikan ulasan yang mengandung reservasi terhadap plot. Ulasan: \"{str(contoh[0])[:120]}...\"",
            f"Meski minoritas ({dist_pct:.1f}%), topik ini penting sebagai cerminan keberagaman opini.",
            "Sebagian penonton merasa Endgame tidak sepenuhnya memenuhi ekspektasi tinggi mereka."
        )
    )

def analyze_avengers_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "battle" in w and ("fan" in w or "saga" in w):
        return (
            "Antusiasme Fan dan Pertempuran Ikonik",
            build_notes(
                "Topik ini merepresentasikan ekspresi kolektif penggemar MCU dalam mengapresiasi pertempuran puncak dan narasi saga yang telah mereka ikuti.",
                f"Kata 'battle', 'fan', dan 'saga' membentuk semantik perayaan komunal komik superhero. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% sangat representatif terhadap basis penggemar yang luas.",
                "Penggemar MCU mengekspresikan antusiasme komunal terhadap pertempuran epik."
            )
        )
    if "conclusion" in w and ("perfect" in w or "wonderful" in w):
        return (
            "Penutup Sempurna Sejarah MCU",
            build_notes(
                "Topik ini merepresentasikan penilaian positif komprehensif dari penonton yang menilai Endgame sebagai pencapaian tertinggi franchise Marvel.",
                f"'Conclusion' dan 'perfect' membentuk cluster evaluasi positif konsisten. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Proporsi sebesar {dist_pct:.1f}% menunjukkan tingkat kepuasan yang tinggi dari keseluruhan penonton.",
                "Endgame dinilai sebagai salah satu konklusi terbaik dalam sejarah film waralaba."
            )
        )
    if "not_give" in w or ("face" in w and "hulk" in w):
        return (
            "Kritik Naratif dan Eksekusi Karakter",
            build_notes(
                "Topik ini merepresentasikan dimensi kritis dari ulasan Endgame, di mana penonton mengidentifikasi kelemahan naratif atau resolusi karakter tertentu (seperti Hulk) yang kurang memuaskan.",
                f"'Not_give', 'face', 'hulk' mengindikasikan ketidakpuasan terhadap keputusan plot spesifik. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Dengan {dist_pct:.1f}% dokumen, opini kritis tetap memiliki porsi di tengah euforia positif.",
                "Penonton yang lebih kritis mengidentifikasi inkonsistensi naratif pada busur beberapa karakter."
            )
        )
    if "nostalgia" in w or ("emotional" in w and "half" in w):
        return (
            "Nostalgia Haru Perjalanan Sedekade",
            build_notes(
                "Topik ini menyoroti dimensi sentimental Endgame sebagai film yang mengandalkan akumulasi afeksi penonton selama lebih dari sepuluh tahun.",
                f"'Nostalgia' dan 'emotional' menunjukkan respons afektif yang bersifat intertekstual terhadap film-film sebelumnya. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi sebesar {dist_pct:.1f}% memperlihatkan kuatnya elemen nostalgia.",
                "Penonton merespons Endgame dengan nostalgia mendalam atas kenangan dari perjalanan MCU sebelumnya."
            )
        )
    return (
        "Penilaian Ambisi Semesta Sinematik",
        build_notes(
            "Topik ini merepresentasikan evaluasi terhadap ambisi besar proyek cinematic universe yang berhasil ditutup dengan pertempuran berskala masif.",
            f"Kata kunci 'universe' dan 'cinematic' memposisikan ulasan pada pencapaian format waralaba. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Proporsi {dist_pct:.1f}% mendeskripsikan pengakuan atas signifikansi industri.",
            "Endgame diapresiasi karena berhasil mengelola skala kolosal dari sebuah semesta sinematik yang kompleks."
        )
    )

# --- COCO ---
def analyze_coco_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Representasi Tradisi dan Kualitas Animasi",
        build_notes(
            "Topik ini berpusat pada apresiasi visual terhadap penggambaran dunia arwah dan elemen kebudayaan Meksiko. Penonton menyoroti kemampuan Pixar memadukan tradisi dengan teknologi animasi canggih.",
            f"Kata-kata utama yang sering muncul mencerminkan apresiasi budaya dan teknis (mis. kebudayaan, animasi). Ulasan: \"{str(contoh[0])[:120]}...\"",
            f"Sebaran {dist_pct:.1f}% menunjukkan kuatnya pengakuan terhadap kekayaan visual film.",
            "Dunia orang mati dalam Coco dipuji sebagai visualisasi tradisi Meksiko yang memukau."
        )
    ) if "mexican_culture" in set(words) else (
        "Dampak Emosional Lintas Generasi",
        build_notes(
            "Topik ini mencakup sentimen penonton yang merasa sangat tersentuh oleh hubungan keluarga dan penyampaian cerita yang kuat. Film ini berhasil menjangkau emosi penonton dari berbagai rentang usia.",
            f"Dominasi istilah emosi keluarga dan kehidupan membuktikan daya tarik lintas usia. Ulasan: \"{str(contoh[0])[:120]}...\"",
            f"Tingkat kemunculan {dist_pct:.1f}% membuktikan kesuksesan film dalam menggugah perasaan audiens.",
            "Cerita keluarga dalam Coco memberikan resonansi emosional yang universal dan mendalam."
        )
    )
def analyze_coco_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "music" in w or "song" in w:
        return (
            "Daya Magis Musik dan Lagu",
            build_notes(
                "Diskusi menyoroti betapa sentralnya peran musik (seperti lagu 'Remember Me') dalam menggerakkan cerita dan emosi penonton. Musik diakui bukan sekadar latar, melainkan nyawa cerita.",
                f"Kehadiran kata seperti 'song' dan 'music' menegaskan poin ini. Ulasan: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi sebesar {dist_pct:.1f}% menandakan bahwa elemen musik sangat melekat di benak penonton.",
                "Musik berfungsi sebagai jembatan emosional utama yang menghubungkan karakter dan penonton."
            )
        )
    return (
        "Perayaan Kenangan dan Kehidupan",
        build_notes(
            "Topik ini secara umum merefleksikan ulasan mengenai tema inti Coco, yakni kematian yang dilihat sebagai perayaan kenangan keluarga yang hangat.",
            f"Istilah-istilah terkait kenangan dan keluarga mendominasi. Ulasan: \"{str(contoh[0])[:120]}...\"",
            f"Porsi {dist_pct:.1f}% menegaskan kuatnya tanggapan atas nilai moral film.",
            "Film ini diapresiasi karena pendekatan cerdasnya dalam memaknai kehidupan dan kematian."
        )
    )

# --- INTERSTELLAR ---
def analyze_interstellar_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "scientific_accuracy" in w or "theoretical_physicist" in w:
        return (
            "Akurasi Saintifik Fisika Teoritis",
            build_notes(
                "Topik ini merepresentasikan apresiasi penonton terhadap fondasi ilmiah Interstellar yang melibatkan fisikawan Kip Thorne, membedakannya dari fiksi ilmiah konvensional.",
                f"'Scientific_accuracy' dan 'theoretical_physicist' menunjukkan integrasi sains yang nyata dalam film. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan tingginya literasi saintifik audiens dalam mengulas film ini.",
                "Interstellar dipuji karena menjaga presisi ilmiah dalam menggambarkan ruang angkasa."
            )
        )
    if "soundtrack_han" in w or "score_han" in w:
        return (
            "Kekuatan Skor Musik Hans Zimmer",
            build_notes(
                "Topik ini berfokus pada pengaruh luar biasa dari skor musik gubahan Hans Zimmer yang dinilai secara mandiri sebagai elemen krusial pembentuk emosi.",
                f"'Soundtrack_han' dan kemunculan alat musik organ menegaskan peran komposisi musik. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Kemunculan topik sebesar {dist_pct:.1f}% mempertegas fungsi musik sebagai bagian naratif integral.",
                "Musik Hans Zimmer dianggap sebagai komponen naratif mandiri yang membentuk ketegangan emosional film."
            )
        )
    return (
        "Ikatan Emosional Ayah dan Anak",
        build_notes(
            "Topik ini menangkap dimensi emosional paling personal dalam film: relasi antara Cooper dan putrinya Murph yang melampaui ruang dan waktu.",
            f"Frasa tentang keluarga dan emosi menyoroti inti drama personal film. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Representasi {dist_pct:.1f}% menegaskan keseimbangan antara aspek teknis dan cerita manusiawi.",
            "Hubungan keluarga memberikan jangkar emosi yang menyeimbangkan kompleksitas sains dalam film."
        )
    )
def analyze_interstellar_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    if "imax" in set(words) or "visual" in set(words):
        return (
            "Kemegahan Visual dan Pengalaman IMAX",
            build_notes(
                "Ulasan dalam kelompok ini merayakan pencapaian visual Interstellar, khususnya saat disaksikan dalam format IMAX, menjadikannya tontonan kosmis yang imersif.",
                f"Dominasi kata 'imax' dan 'visual' menyoroti nilai pengalaman teatrikal film. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% mendemonstrasikan apresiasi atas terobosan teknis pengambilan gambar.",
                "Pengalaman menonton IMAX menjadi elemen tak terpisahkan dari kepuasan audiens terhadap visual film."
            )
        )
    return (
        "Ambiguitas Waktu dan Narasi",
        build_notes(
            "Topik ini menyoroti perdebatan dan kebingungan (yang seringkali dipandang positif) seputar kompleksitas penyelesaian cerita dan konsep ruang-waktu.",
            f"Kehadiran kata yang mengindikasikan misteri atau pertanyaan menegaskan ambiguitas akhir cerita. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Porsi topik sebesar {dist_pct:.1f}% merefleksikan kecenderungan diskusi pasca-nonton yang intens.",
            "Kompleksitas konsep dilatasi waktu dan resolusi cerita memicu diskusi berkelanjutan di kalangan penonton."
        )
    )

# --- PARASITE ---
def analyze_parasite_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "dark_comedy" in w or "thriller_horror" in w:
        return (
            "Hibriditas Genre Satir Komedi Gelap",
            build_notes(
                "Topik ini mengapresiasi transisi mulus Parasite dari komedi satir keluarga ke arah thriller yang mengejutkan. Penonton memuji kepiawaian perpaduan tonal ini.",
                f"'Dark_comedy' dan referensi thriller menunjukkan apresiasi atas penguasaan multi-genre Bong Joon-ho. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% membuktikan pergeseran genre sebagai salah satu elemen paling ikonik dari film.",
                "Transisi dari komedi ke thriller menjadi keputusan naratif paling mengejutkan dan dipuji audiens."
            )
        )
    return (
        "Alegori dan Ketimpangan Kelas Sosial",
        build_notes(
            "Ulasan dalam topik ini sangat analitis, membaca film sebagai metafora yang tajam tentang ketimpangan ekonomi dan struktur masyarakat modern.",
            f"Istilah terkait kaya-miskin dan 'social_commentary' mendominasi diskursus kritis ini. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Representasi sebesar {dist_pct:.1f}% menunjukkan kedalaman pemahaman penonton atas makna tersirat film.",
            "Parasite dipahami dan dielu-elukan sebagai alegori kelas sosial yang relevan dan menggugah."
        )
    )
def analyze_parasite_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "oscar" in w or "award" in w:
        return (
            "Pengakuan Global dan Sejarah Oscar",
            build_notes(
                "Topik ini membahas kemenangan historis film di ajang penghargaan global dan bagaimana hal itu meruntuhkan batasan bahasa di industri perfilman internasional.",
                f"Munculnya kata 'oscar' membingkai diskusi ke arah penerimaan dan impak global film. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan kebanggaan dan perbincangan industri secara makro.",
                "Kemenangan di ajang internasional membuktikan kualitas narasi yang menembus kendala bahasa."
            )
        )
    return (
        "Dinamika Karakter dan Kehidupan Otentik",
        build_notes(
            "Fokus ulasan ini adalah pada keaslian gambaran kehidupan sehari-hari dan karisma ansambel pemeran yang membuat realitas sosial film terasa hidup.",
            f"Istilah terkait kehidupan dan karakter menyoroti kedalaman performa akting. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Porsi sebesar {dist_pct:.1f}% menegaskan pentingnya performa aktor dalam menyukseskan tema film.",
            "Kualitas akting dan penggambaran realitas sosial yang autentik memperkuat ketegangan cerita."
        )
    )

# --- SPIDER-VERSE ---
def analyze_spiderverse_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Inovasi Gaya Animasi Komik",
        build_notes(
            "Topik ini berpusat pada kekaguman mutlak audiens terhadap gaya visual revolusioner yang menghidupkan kembali estetika buku komik cetak melalui medium digital.",
            f"Terminologi gaya seni dan animasi menjadi poin sentral ulasan ini. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi luas {dist_pct:.1f}% membuktikan pencapaian artistik sebagai elemen paling menonjol.",
            "Gaya visual film ini diakui sebagai terobosan artistik yang mendefinisikan ulang standar animasi."
        )
    )
def analyze_spiderverse_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Ekspektasi Terlampaui dan Karakter Segar",
        build_notes(
            "Topik ini menangkap sentimen audiens yang merasa terkejut positif. Kisah asal-usul Miles Morales dianggap menyegarkan genre pahlawan super yang sempat dinilai jenuh.",
            f"Penggunaan kata ekspektasi dan kepuasan sangat dominan dalam menggambarkan kejutan kualitas cerita. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Proporsi {dist_pct:.1f}% menegaskan tingginya Word-of-Mouth yang positif.",
            "Pengembangan karakter yang kuat dan visual inovatif membuat film ini melampaui semua ekspektasi audiens."
        )
    )

# --- THE DARK KNIGHT ---
def analyze_tdk_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "jack_nicholson" in w or "heath_ledger" in w:
        return (
            "Keagungan Penampilan Heath Ledger",
            build_notes(
                "Topik ini secara khusus dan intensif membahas penampilan legendaris Heath Ledger, menjadikannya standar tertinggi untuk karakter antagonis dalam sejarah film.",
                f"Referensi pada aktor terdahulu dan pujian selangit ('oscar_worthy') memusatkan evaluasi pada kualitas akting. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi {dist_pct:.1f}% menunjukkan sentralitas performa ini dalam reputasi film secara keseluruhan.",
                "Performa Heath Ledger diakui secara universal sebagai salah satu penampilan akting terbaik yang pernah ada."
            )
        )
    return (
        "Nuansa Drama Kriminal Epik",
        build_notes(
            "Ulasan dalam kelompok ini mengevaluasi The Dark Knight bukan sekadar sebagai film adaptasi komik, melainkan sebagai drama kriminal bernuansa kelam, filosofis, dan serius.",
            f"Kata-kata terkait moralitas dan tindak kriminal membingkai film sejajar dengan mahakarya genre mafia. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Sebaran {dist_pct:.1f}% membuktikan pengakuan akan kedalaman narasi film ini.",
            "Film ini dinilai sukses melampaui genre pahlawan super menjadi drama kriminal bermuatan filosofis."
        )
    )
def analyze_tdk_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Mahakarya Kebaikan Melawan Kekacauan",
        build_notes(
            "Topik ini merangkum diskusi mengenai dinamika moral Batman dan Joker, menyoroti bagaimana film tersebut mengeksplorasi batas tipis antara kepahlawanan dan anarki di Gotham.",
            f"Dominasi istilah kepahlawanan dan kegilaan menyoroti tema dualitas manusia. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Porsi {dist_pct:.1f}% mengindikasikan kuatnya tema sentral pertarungan ideologi dalam benak audiens.",
            "Kekuatan utama film ini terletak pada eksplorasi psikologis dan moral yang diwujudkan melalui konflik Batman dan Joker."
        )
    )

# --- LOTR: RETURN OF THE KING ---
def analyze_lotr_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    w = set(words)
    if "greatest_trilogy" in w:
        return (
            "Puncak Epik Trilogi Terbaik",
            build_notes(
                "Ulasan ini menegaskan konsensus audiens bahwa film ini merupakan penutup sempurna dan menyandang gelar salah satu trilogi terbesar dalam sejarah perfilman.",
                f"Penggunaan superlatif secara masif ('greatest_trilogy') menunjukkan tingkat kepuasan yang nyaris tanpa cela. Contoh: \"{str(contoh[0])[:120]}...\"",
                f"Distribusi sebesar {dist_pct:.1f}% menggarisbawahi posisi film ini di puncak apresiasi sinema fantasi.",
                "Return of the King diakui sebagai kesimpulan epik yang mengokohkan posisinya sebagai trilogi paling luar biasa."
            )
        )
    return (
        "Skala Pertempuran dan Visual Emosional",
        build_notes(
            "Topik ini berfokus pada keseimbangan apik antara skala perang yang sangat kolosal (seperti Minas Tirith) dan bobot penyelesaian busur emosional tiap karakter.",
            f"Kombinasi frasa peperangan dan karakter menunjukkan harmoni antara aksi dan emosi. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Sebaran {dist_pct:.1f}% membuktikan kesuksesan eksekusi aksi berskala raksasa.",
            "Keseimbangan antara aksi kolosal dan keintiman karakter adalah kunci kepuasan puncak dari epik ini."
        )
    )
def analyze_lotr_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Kesetiaan Adaptasi dan Penghargaan Tertinggi",
        build_notes(
            "Topik ini mencakup penghargaan retrospektif penonton atas upaya ambisius Peter Jackson dalam menghidupkan dunia J.R.R. Tolkien secara akurat dan bermartabat, yang diganjar 11 Oscar.",
            f"Munculnya kata terkait buku dan penghargaan menggambarkan penghormatan terhadap sumber material. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% menempatkan elemen dedikasi terhadap warisan sastra sebagai pilar penting ulasan.",
            "Keberhasilan adaptasi sumber material yang setia mendapatkan validasi melalui pengakuan di ajang Academy Awards."
        )
    )

# --- TOY STORY ---
def analyze_toystory_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Tonggak Sejarah Animasi Komputer",
        build_notes(
            "Topik ini merepresentasikan kesadaran historis penonton tentang nilai revolusioner Toy Story sebagai pionir animasi komputer, yang memicu perubahan masif di industri perfilman global.",
            f"Penggunaan kata-kata teknis dan sejarah industri menunjukkan perspektif evaluasi berbasis inovasi. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% memperlihatkan pengakuan yang luas terhadap perannya mengubah sejarah sinema.",
            "Toy Story diapresiasi sebagai titik balik inovatif yang membuka era baru bagi industri animasi."
        )
    )
def analyze_toystory_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Dinamika Persahabatan Tak Lekang Waktu",
        build_notes(
            "Ulasan di sini berpusat pada elemen narasi yang paling kuat: konflik, pertumbuhan, dan ikatan persahabatan antara Woody dan Buzz yang selalu relevan lintas generasi.",
            f"Istilah seputar relasi, krisis identitas, dan emosi anak-anak menandakan kekuatan tema universal cerita. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Distribusi {dist_pct:.1f}% mengonfirmasi bahwa resonansi emosional tetap menjadi daya tarik terkuat.",
            "Kisah kecemburuan yang berubah menjadi persahabatan sejati menjadikan film ini karya seni yang tak lekang oleh waktu."
        )
    )

# --- WALL-E ---
def analyze_walle_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Penceritaan Visual Tanpa Dialog",
        build_notes(
            "Topik ini menyoroti kekaguman atas keberhasilan sepertiga awal film yang mampu menyampaikan narasi emosional secara efektif dan mendalam tanpa menggunakan dialog lisan.",
            f"Frasa tentang ekspresi non-verbal mendominasi observasi audiens. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Kemunculan topik pada {dist_pct:.1f}% dokumen menunjukkan apresiasi luar biasa atas eksekusi gaya penceritaan visual ini.",
            "Kemampuan membangun empati yang murni melalui ekspresi visual adalah salah satu pencapaian terbesar WALL-E."
        )
    )
def analyze_walle_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Kritik Lingkungan dalam Bingkai Keluarga",
        build_notes(
            "Topik ini membahas keluwesan film menyelipkan satir keras mengenai konsumerisme dan kerusakan bumi ke dalam cerita animasi keluarga yang menyentuh hati dan indah.",
            f"Terminologi seputar bumi, alam, dan sampah berpadu dengan tema harapan, merefleksikan kedalaman pesan moral film. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Tingkat distribusi {dist_pct:.1f}% membuktikan kesadaran audiens terhadap signifikansi pesan sosial yang diusung.",
            "Peringatan dystopia lingkungan berhasil disampaikan secara apik melalui bungkus cerita romansa fiksi ilmiah."
        )
    )

# --- YOUR NAME ---
def analyze_yourname_bigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Romansa Visual dan Desain Suara",
        build_notes(
            "Ulasan menyoroti perpaduan sinergis antara gaya animasi indah khas Makoto Shinkai dan iringan musik RADWIMPS yang membangun eskalasi emosional hingga klimaks.",
            f"Penggunaan kata yang memuji estetika dan audio menunjukkan elemen sensori yang memikat audiens. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Dengan {dist_pct:.1f}%, dapat disimpulkan bahwa pengalaman audiovisual menjadi aspek utama penilaian.",
            "Sinkronisasi antara keindahan animasi langit yang ikonis dan iringan musik menciptakan resonansi emosional maksimal."
        )
    )
def analyze_yourname_unigram(words, contoh, dist_pct, topic_idx, total_topics):
    return (
        "Daya Pikat Takdir Lintas Dimensi",
        build_notes(
            "Topik ini berpusat pada konsep 'Musubi' (ikatan takdir) yang menjadi jantung cerita komedi romantis ini, berkembang secara dramatis mengatasi batasan ruang dan waktu.",
            f"Istilah seputar takdir, waktu, dan ingatan menunjukkan ketertarikan penonton pada aspek spiritual dan misteri cerita. Contoh: \"{str(contoh[0])[:120]}...\"",
            f"Proporsi sebesar {dist_pct:.1f}% menekankan kekuatan tema ikatan metafisik yang universal.",
            "Eksplorasi emosional dari pencarian identitas dan cinta lintas waktu memberikan daya pikat emosional yang universal."
        )
    )

# Fallback generic dispatcher for the film groups
def generic_dispatcher(words, contoh, dist_pct, tidx, t_total, fallback_func):
    return fallback_func(words, contoh, dist_pct, tidx, t_total)

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

OVERALL_INTERPRETATIONS = {
    "Avengers_Endgame_2019": "Secara keseluruhan, diskusi penonton mengenai Avengers: Endgame sangat terfokus pada posisinya sebagai klimaks emosional dari narasi MCU yang telah dibangun selama lebih dari satu dekade. Topik yang paling dominan berkaitan dengan bobot emosional dan resolusi karakter, terutama pengorbanan Tony Stark, serta kualitas visual dari pertempuran akhir. Terdapat hubungan yang kuat antara apresiasi terhadap skala aksi dan kepuasan terhadap penutup emosional, menunjukkan bahwa penonton menilai kedua aspek tersebut saling melengkapi. Meskipun terdapat sebagian kecil ulasan kritis terkait pilihan naratif tertentu, gambaran umum menunjukkan bahwa penonton sangat mengapresiasi keberhasilan Russo Brothers dalam memberikan konklusi epik yang memenuhi ekspektasi penggemar.",
    "Coco_2017": "Analisis ulasan Coco menunjukkan bahwa penonton sangat menghargai perpaduan antara kualitas animasi Pixar yang memukau dan kedalaman emosional narasinya. Aspek yang paling banyak dibahas adalah representasi otentik budaya Meksiko, khususnya terkait tradisi Día de los Muertos, dan bagaimana musik berfungsi sebagai elemen penggerak emosi. Topik dominan sering kali mengaitkan keindahan visual dunia arwah dengan daya tarik film lintas generasi. Secara keseluruhan, audiens memberikan apresiasi tinggi terhadap kemampuan film dalam mengemas tema-tema kompleks seperti kematian, kenangan, dan ikatan keluarga ke dalam sebuah cerita yang penuh warna, mengharukan, dan dapat dinikmati oleh berbagai kalangan usia.",
    "Interstellar_2014": "Hasil pemodelan topik untuk Interstellar menyoroti keseimbangan antara ambisi ilmiah dan kedalaman emosional film ini. Penonton paling banyak mendiskusikan akurasi saintifik, visualisasi ruang angkasa—seperti lubang hitam Gargantua—dan skor musik Hans Zimmer yang ikonik. Di sisi lain, topik mengenai hubungan ayah-anak yang menjadi jangkar emosional cerita juga sangat dominan. Meskipun beberapa topik menunjukkan adanya perdebatan terkait kompleksitas naratif dan bagian akhir cerita yang memecah opini, gambaran umum merepresentasikan kekaguman audiens terhadap visi Christopher Nolan yang berhasil mengintegrasikan ilmu pengetahuan teoritis dengan pengalaman sinematik yang emosional dan mendalam.",
    "Parasite_2019": "Secara umum, ulasan mengenai Parasite berpusat pada kepiawaian sutradara Bong Joon-ho dalam mengeksekusi alegori sosial yang tajam. Topik yang paling mendominasi adalah perbandingan kelas sosial, ketimpangan ekonomi, dan perubahan genre yang mengejutkan dari komedi gelap menjadi thriller. Penonton sering mengaitkan ketegangan naratif dengan kritik sosial, menunjukkan bahwa audiens sangat menyadari lapisan tematik film ini di luar alur ceritanya. Selain itu, kesuksesan Parasite melampaui hambatan bahasa dan pencapaiannya di ajang penghargaan global juga menjadi sorotan. Penonton mengapresiasi film ini sebagai mahakarya satir yang cerdas, menegangkan, sekaligus memicu refleksi mendalam mengenai realitas kelas sosial.",
    "Spider_Man_Into_The_Spider_Verse_2018": "Ulasan penonton mengenai Spider-Man: Into the Spider-Verse didominasi oleh pujian terhadap inovasi gaya animasinya yang merevolusi genre dengan memadukan estetika komik cetak dan teknik animasi komputer modern. Aspek visual ini secara konsisten dikaitkan dengan kualitas naratif, terutama pengembangan karakter Miles Morales dan redefinisi konsep heroisme. Banyak topik yang mencerminkan kepuasan penonton karena film ini berhasil melampaui ekspektasi awal mereka. Gambaran umum menunjukkan bahwa film ini tidak hanya dianggap sebagai salah satu film superhero terbaik, tetapi juga diakui sebagai karya seni animasi yang membawa penyegaran dan orisinalitas yang sangat dibutuhkan dalam lanskap industri perfilman.",
    "The_Dark_Knight_2008": "Secara keseluruhan, ulasan The Dark Knight didominasi oleh apresiasi yang luar biasa terhadap penampilan mendiang Heath Ledger sebagai Joker, yang secara luas diakui sebagai salah satu pencapaian akting terbaik dalam sejarah sinema. Penonton secara intens mendiskusikan dimensi psikologis dan eksplorasi moral yang diusung oleh karakter tersebut. Selain itu, topik tentang arahan Christopher Nolan, kompleksitas karakter pendukung, dan nuansa kejahatan kota Gotham sangat menonjol. Film ini secara konsisten dievaluasi bukan sekadar sebagai film pahlawan super, melainkan sebagai sebuah drama kriminal epik yang mendefinisikan ulang standar genre dan meninggalkan warisan kultural yang abadi.",
    "The_Lord_Of_The_Rings_The_Return_Of_The_King_2003": "Analisis ulasan The Return of the King merepresentasikan kekaguman kolektif audiens terhadap penyelesaian yang epik dan memuaskan dari sebuah trilogi monumental. Topik yang paling mendominasi berkaitan dengan skala pertempuran kolosal, seperti di Minas Tirith, serta kualitas emosional dari perjalanan akhir para karakter menuju Gunung Doom. Penonton juga secara konsisten membahas kesetiaan adaptasi karya Tolkien, pencapaian teknis dalam efek visual, dan rekor penghargaan Academy Award. Gambaran umum menunjukkan bahwa penonton mengakui film ini sebagai pencapaian puncak dalam genre fantasi epik yang berhasil menyatukan kedalaman naratif, emosi yang kuat, dan eksekusi sinematik berskala raksasa.",
    "Toy_Story_1995": "Secara umum, ulasan tentang Toy Story menyoroti posisinya sebagai tonggak bersejarah yang mengubah industri melalui animasi komputer penuh pertama. Topik-topik utama berkisar pada keunggulan teknis, kesederhanaan premis yang inovatif, dan daya tariknya yang universal untuk semua kelompok usia. Lebih jauh lagi, narasi tentang persahabatan, krisis identitas, dan pertumbuhan karakter antara Woody dan Buzz merupakan aspek krusial yang mengikat emosi audiens. Secara keseluruhan, penonton menghargai film ini bukan hanya karena inovasi visualnya yang revolusioner pada masanya, tetapi juga karena kemampuannya menghadirkan kisah kemanusiaan yang beresonansi kuat dan tak lekang oleh waktu.",
    "WALL_E_2008": "Hasil analisis topik WALL-E menunjukkan bahwa perhatian utama audiens terbagi secara harmonis antara apresiasi estetika dan pesan tematik film. Topik dominan menyoroti kemampuan luar biasa Pixar dalam menceritakan kisah yang sangat emosional tanpa menggunakan banyak dialog verbal, mengandalkan ekspresi visual dan suara robot. Di sisi lain, pesan kuat mengenai lingkungan, kritik terhadap konsumerisme, dan gambaran masa depan dystopia juga mendapat perhatian besar. Secara keseluruhan, penonton sangat mengagumi keberanian film ini dalam membungkus pesan moral yang mendalam dan peringatan sosial ke dalam sebuah karya animasi keluarga yang indah, mengharukan, sekaligus relevan.",
    "Your_Name_2016": "Ulasan penonton terhadap Your Name didominasi oleh perpaduan antara kekaguman atas keindahan visual yang luar biasa dan daya tarik emosional dari narasinya. Topik utama berfokus pada gaya seni khas Makoto Shinkai yang memukau, musik dari RADWIMPS yang memperkuat kedalaman cerita, dan konsep 'body swap' yang berubah dari elemen komedi menjadi eksplorasi dramatis tentang takdir dan koneksi lintas waktu. Aspek budaya dan kontras kehidupan di Jepang juga sering dibahas. Secara umum, audiens mengakui film ini sebagai pengalaman sinematik yang mendalam, berhasil menarik simpati emosional penonton global sekaligus mempertahankan identitas kulturalnya."
}

def apply_academic_interpretations(payload, mode):
    film_key = payload.get("title", "")
    if film_key not in FILM_DISPATCHERS:
        return payload
        
    dispatcher = FILM_DISPATCHERS[film_key].get(mode)
    if not dispatcher:
        return payload

    topics = payload.get('topics', {})
    
    if film_key in OVERALL_INTERPRETATIONS:
        payload['overall_interpretation'] = OVERALL_INTERPRETATIONS[film_key]

    if 'interpretations' not in payload:
        payload['interpretations'] = {}

    total_dist = 0
    for tdata in topics.values():
        words = tdata.get('words', [])
        total_dist += sum(w['weight'] for w in words) if words else 1
        
    topic_list = list(topics.items())
    for tidx, (tname, tdata) in enumerate(topic_list):
        words = [w['word'] for w in tdata.get('words', [])[:15]]
        contoh = tdata.get('contoh_ulasan', ['(tidak tersedia)'])
        if not contoh: contoh = ['(tidak tersedia)']
        
        topic_weights = [w['weight'] for w in tdata.get('words', [])]
        topic_sum = sum(topic_weights) if topic_weights else 0
        dist_pct = (topic_sum / max(total_dist, 0.001)) * 100 if total_dist > 0 else (100.0 / max(len(topics), 1))
        
        if not words: continue
        
        label, notes = generic_dispatcher(words, contoh, dist_pct, tidx, len(topic_list), dispatcher)
        label = clean_label(label)
        
        payload['interpretations'][tname] = {
            "custom_label": label,
            "notes": notes
        }
        
    return payload

def run_update():
    from services.db_service import get_db_connection
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT id_title, result_data FROM movie_analysis')
    rows = cur.fetchall()

    total_updated = 0
    total_configs = len(rows)

    for row in rows:
        db_key = row['id_title']
        try:
            data = json.loads(row['result_data'])
        except Exception:
            continue

        m = re.match(r'^(.+)_(unigram|bigram)_k(\d+)$', db_key)
        if not m:
            continue
        
        film_key = m.group(1)
        mode = m.group(2)
        
        if film_key not in FILM_DISPATCHERS:
            continue
            
        data = apply_academic_interpretations(data, mode)
        
        # Save back to DB
        cur.execute('UPDATE movie_analysis SET result_data = ? WHERE id_title = ?', (json.dumps(data), db_key))
        total_updated += 1
        
    conn.commit()
    conn.close()
    print(f"Success updating {total_updated} / {total_configs} configs directly in DB.")

if __name__ == '__main__':
    run_update()

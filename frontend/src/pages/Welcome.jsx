import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const GUIDE_STEPS = [
  {
    title: 'Siapkan Dataset',
    desc: 'Kumpulkan ulasan film dari IMDb menggunakan ekstensi web scraper, lalu simpan hasilnya sebagai satu file.',
  },
  {
    title: 'Format File',
    desc: 'Pastikan file berformat .CSV dan memiliki minimal satu kolom yang berisi teks ulasan penonton.',
  },
  {
    title: 'Unggah & Pilih Kolom',
    desc: 'Unggah file CSV di menu Upload, lalu pilih nama kolom yang memuat teks ulasan. Sistem akan menampilkan pratinjau 5 baris data pertama.',
  },
  {
    title: 'Preprocessing Otomatis',
    desc: 'Sistem membersihkan teks secara bertahap (penyamaan huruf kecil, penghapusan simbol, tokenisasi, penghapusan kata umum, hingga penyederhanaan kata dasar). Setiap tahap bisa dilihat pratinjaunya.',
  },
  {
    title: 'Jalankan Analisis Topik',
    desc: 'Masukkan judul film, lalu jalankan analisis. Sistem otomatis menguji 2 hingga 10 topik dengan dua cara pembacaan kata (kata tunggal & pasangan kata), dan memilih hasil terbaik secara otomatis.',
  },
  {
    title: 'Baca Hasil Analisis',
    desc: 'Lihat topik-topik yang ditemukan lengkap dengan kata kunci dominan, skor kualitas topik, grafik perbandingan, serta interpretasi otomatis dari tiap topik.',
  },
  {
    title: 'Riwayat & Unduh',
    desc: 'Buka menu History untuk melihat kembali seluruh analisis yang pernah dijalankan, atau unduh hasilnya dalam format CSV kapan saja.',
  },
];

function Welcome() {
  const [showGuide, setShowGuide] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="w-full min-h-screen flex items-center justify-center p-6 font-sans">
      <div className="w-full max-w-3xl flex flex-col items-center">
        <div
          className="card-container w-full text-center flex flex-col items-center transition-all duration-500"
          style={{ padding: '50px 40px' }}
        >
          <h1 className="page-title" style={{ fontSize: '38px', marginBottom: '20px', lineHeight: '1.2' }}>
            Analisis Topik Ulasan Film
          </h1>

          <p className="text-muted" style={{ fontSize: '16px', maxWidth: '600px', marginBottom: '35px' }}>
            Temukan topik-topik dominan secara otomatis dari dataset ulasan penonton menggunakan pemodelan
            <strong style={{ color: '#000', fontWeight: '600' }}> Latent Dirichlet Allocation (LDA)</strong>.
          </p>

          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap', width: '100%' }}>
            <button
              onClick={() => navigate('/home')}
              className="btn-primary"
              style={{ padding: '12px 28px', fontSize: '15px' }}
            >
              Mulai Analisis
            </button>

            <button
              onClick={() => setShowGuide(!showGuide)}
              className="btn-browse"
              style={{ padding: '12px 28px', fontSize: '15px' }}
              aria-expanded={showGuide}
            >
              {showGuide ? 'Tutup Petunjuk' : 'Petunjuk Penggunaan'}
            </button>
          </div>

          {showGuide && (
            <div
              style={{
                marginTop: '35px',
                textAlign: 'left',
                width: '100%',
                borderTop: '1px solid #e0e0e0',
                paddingTop: '30px',
                animation: 'fadeIn 0.3s ease-in-out',
              }}
            >
              <h3
                className="section-title"
                style={{ marginTop: 0, marginBottom: '22px', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <span
                  style={{ width: '6px', height: '22px', backgroundColor: '#000', borderRadius: '4px', display: 'inline-block' }}
                />
                Cara Menggunakan Aplikasi
              </h3>

              <ol style={{ listStyle: 'none', margin: 0, padding: 0 }}>
                {GUIDE_STEPS.map((step, idx) => (
                  <li
                    key={step.title}
                    style={{
                      display: 'flex',
                      gap: '16px',
                      alignItems: 'flex-start',
                      paddingBottom: idx === GUIDE_STEPS.length - 1 ? 0 : '18px',
                      marginBottom: idx === GUIDE_STEPS.length - 1 ? 0 : '18px',
                      borderBottom: idx === GUIDE_STEPS.length - 1 ? 'none' : '1px dashed #e5e5e5',
                    }}
                  >
                    <span
                      style={{
                        flexShrink: 0,
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        backgroundColor: '#000',
                        color: '#fff',
                        fontSize: '13px',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {idx + 1}
                    </span>
                    <div>
                      <div style={{ fontSize: '15px', fontWeight: 600, color: '#222', marginBottom: '4px' }}>
                        {step.title}
                      </div>
                      <div className="text-muted" style={{ fontSize: '14px', lineHeight: '1.55' }}>
                        {step.desc}
                      </div>
                    </div>
                  </li>
                ))}
              </ol>

              <p
                className="text-muted"
                style={{
                  fontSize: '13px',
                  marginTop: '22px',
                  paddingTop: '18px',
                  borderTop: '1px solid #e0e0e0',
                }}
              >
                Butuh penjelasan istilah teknis seperti "skor kualitas topik"? Setiap istilah pada halaman hasil
                dilengkapi keterangan singkat yang bisa dibuka dengan menekan ikon (?) di sebelahnya.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Welcome;

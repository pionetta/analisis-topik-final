import { useContext } from 'react';
import { AppContext } from '../context/AppContext';
import { Link } from 'react-router-dom';

function Preprocessing() {
  const { prepSteps } = useContext(AppContext);

  // Fungsi untuk memotong teks yang terlalu panjang agar tabel tetap ringkas
  const truncateText = (text, maxLength = 100) => {
    if (!text) return <span style={{ color: '#d4d4d4', fontStyle: 'italic' }}>[Teks kosong/terhapus]</span>;
    const str = String(text);
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
  };

  return (
    <div>
      <h1 style={{ fontSize: '24px', marginBottom: '25px', color: 'var(--text-primary)' }}>Preprocessing Teks</h1>

      {!prepSteps || !prepSteps.original ? (
        <div className="card-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ fontSize: '40px', marginBottom: '15px' }}>📂</div>
          <h3 style={{ color: 'var(--text-primary)', margin: '0 0 10px 0', fontSize: '18px' }}>Belum Ada Data Diproses</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '25px' }}>
            Silakan unggah dataset terlebih dahulu untuk melihat hasil tahapan pembersihan teks.
          </p>

          <Link to="/home" className="btn-primary" style={{ textDecoration: 'none' }}>
            Kembali ke Halaman Upload
          </Link>
        </div>
      ) : (
        <div className="card-container" style={{ overflow: 'hidden' }}>
          <div style={{ marginBottom: '25px' }}>
            <h3 style={{ marginTop: 0, color: 'var(--text-primary)', fontSize: '16px', marginBottom: '8px' }}>
              Tabel Perbandingan Hasil Preprocessing
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
              Menampilkan 5 sampel ulasan. <br />
            </p>
          </div>

          {prepSteps.stats && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '16px',
              marginBottom: '30px'
            }}>
              {[
                { label: 'Total Dokumen', value: prepSteps.stats.total_docs_valid, sub: `dari ${prepSteps.stats.total_docs_raw} raw` },
                { label: 'Dokumen Kosong/Dibuang', value: prepSteps.stats.total_dropped },
                { label: 'Vocabulary Unik', value: prepSteps.stats.vocab_size },
                { label: 'Total Token', value: prepSteps.stats.total_tokens },
                { label: 'Rata-rata Token / Dokumen', value: prepSteps.stats.avg_tokens },
              ].map((stat, i) => (
                <div key={i} style={{
                  backgroundColor: 'var(--bg-app)', border: '1px solid var(--border-light)',
                  padding: '16px', borderRadius: '10px', textAlign: 'center'
                }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '500', marginBottom: '8px' }}>{stat.label}</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--text-primary)' }}>{stat.value.toLocaleString()}</div>
                  {stat.sub && <div style={{ fontSize: '11px', color: '#a2a2a2', marginTop: '4px' }}>{stat.sub}</div>}
                </div>
              ))}
            </div>
          )}

          <div style={{ width: '100%', overflowX: 'auto', paddingBottom: '10px' }}>
            <table style={{ width: '100%', minWidth: '1200px', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e6e6e6', textAlign: 'left' }}>
                  <th style={{ width: '50px', textAlign: 'center', padding: '12px 8px', color: '#535353' }}>No</th>
                  <th style={{ minWidth: '220px', padding: '12px 8px', color: '#535353' }}>Original</th>
                  <th style={{ minWidth: '220px', padding: '12px 8px', color: '#535353' }}>Case Folding</th>
                  <th style={{ minWidth: '220px', padding: '12px 8px', color: '#535353' }}>Cleansing</th>
                  <th style={{ minWidth: '220px', padding: '12px 8px', color: '#535353' }}>Stopword</th>
                  <th style={{ minWidth: '220px', padding: '12px 8px', color: '#535353' }}>Lemmatization</th>
                </tr>
              </thead>
              <tbody>
                {prepSteps.original.map((_, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #f3f3f3' }}>
                    <td style={{ textAlign: 'center', color: '#a2a2a2', padding: '12px 8px' }}>{i + 1}</td>


                    <td title={prepSteps.original?.[i]} style={{ fontSize: '13px', lineHeight: '1.6', color: '#717171', padding: '12px 8px' }}>
                      {truncateText(prepSteps.original?.[i])}
                    </td>
                    <td title={prepSteps.case_folding?.[i]} style={{ fontSize: '13px', lineHeight: '1.6', color: '#717171', padding: '12px 8px' }}>
                      {truncateText(prepSteps.case_folding?.[i])}
                    </td>
                    <td title={prepSteps.cleansing?.[i]} style={{ fontSize: '13px', lineHeight: '1.6', color: '#717171', padding: '12px 8px' }}>
                      {truncateText(prepSteps.cleansing?.[i])}
                    </td>
                    <td title={prepSteps.stopword?.[i]} style={{ fontSize: '13px', lineHeight: '1.6', color: '#717171', padding: '12px 8px' }}>
                      {truncateText(prepSteps.stopword?.[i])}
                    </td>
                    <td title={prepSteps.lemmatization?.[i]} style={{ fontSize: '13px', lineHeight: '1.6', color: '#717171', padding: '12px 8px' }}>
                      {truncateText(prepSteps.lemmatization?.[i])}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>


          <div style={{ marginTop: '30px', textAlign: 'right', borderTop: '1px solid #e6e6e6', paddingTop: '20px' }}>
            <Link
              to="/analysis"
              className="btn-primary"
              style={{ textDecoration: 'none', display: 'inline-block', padding: '10px 20px', fontSize: '15px' }}
            >
              Lanjut ke Analisis Topik
            </Link>
          </div>

        </div>
      )}
    </div>
  );
}

export default Preprocessing;
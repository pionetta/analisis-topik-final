/* eslint-disable no-unused-vars */
import { useContext, useEffect, useState, useCallback } from 'react';
import { AppContext } from '../context/AppContext';
import AnalysisResultView from '../components/AnalysisResultView';

/**
 * Dialog Konfirmasi â€” menggantikan window.confirm() yang primitif.
 */
function ConfirmDialog({ message, onConfirm, onCancel }) {
  return (
    <div className="confirm-overlay" onClick={onCancel}>
      <div className="confirm-box" onClick={(e) => e.stopPropagation()}>
        <h3>Konfirmasi Hapus</h3>
        <p>{message}</p>
        <div className="confirm-actions">
          <button onClick={onCancel} className="btn-browse">Batal</button>
          <button onClick={onConfirm} className="btn-danger">Hapus Semua</button>
        </div>
      </div>
    </div>
  );
}

function History() {
  const {
    API_BASE_URL,
    savedMovies,
    fetchSavedMovies,
    showToast,
  } = useContext(AppContext);

  const [isLoading, setIsLoading] = useState(false);
  const [viewedResult, setViewedResult] = useState(null);
  const [confirmState, setConfirmState] = useState(null); // { message, onConfirm }

  useEffect(() => {
    fetchSavedMovies();
    const interval = setInterval(() => {
      fetchSavedMovies();
    }, 4000);
    return () => clearInterval(interval);
  }, [fetchSavedMovies]);

  // LOGIKA PENGELOMPOKAN HISTORY BERDASARKAN JUDUL
  // savedMovies sekarang berupa array of { id_title, optimal_k }
  const groupedMovies = savedMovies.reduce((acc, item) => {
    const key = item.id_title ?? item; // backward-compat jika masih string
    const optK = item.optimal_k ?? null;

    // [PERBAIKAN] Gunakan regex yang cocok dari belakang string untuk menghindari
    // konflik dengan judul film yang mengandung "_k" (misal: "The_Dark_Knight").
    // Format key: "{title}_{mode}_k{angka}" â€” misal: "The_Dark_Knight_2008_bigram_k3"
    const match = key.match(/^(.+)_(unigram|bigram)_k(\d+)$/);
    let title = key, k = '-';
    if (match) {
      title = match[1].replace(/_/g, ' '); // underscore â†’ spasi
      k = match[3];                         // angka K
    }
    if (!acc[title]) acc[title] = { items: [], optimalK: optK };
    // Ambil optimal_k dari item manapun dalam grup (semua entri satu grup punya nilai sama)
    if (optK !== null && acc[title].optimalK === null) acc[title].optimalK = optK;
    // [PERBAIKAN BUG-04] Ekstrak mode agar item bisa dibedakan secara unik (K + mode)
    const modeFromKey = key.match(/_(unigram|bigram)_k\d+$/)?.[1] || '';
    acc[title].items.push({ k: parseInt(k) || 0, raw: key, displayK: k, mode: modeFromKey, is_empty: item.is_empty });
    return acc;
  }, {});

  Object.keys(groupedMovies).forEach(title => {
    groupedMovies[title].items.sort((a, b) => a.k - b.k);
  });

  const handleLoadHistory = async (dbKey) => {
    setIsLoading(true);
    setViewedResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/saved_movies/${dbKey}`);
      if (!response.ok) {
        showToast(`Gagal memuat: Server Error ${response.status}`, 'error');
        return;
      }
      const data = await response.json();
      if (data.status === 'success') {
        setViewedResult(data.data);
      } else {
        showToast(`Gagal memuat history: ${data.error}`, 'error');
      }
    } catch {
      showToast("Gagal terhubung ke server backend Flask.", 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteGroup = (title, items) => {
    setConfirmState({
      message: `Apakah Anda yakin ingin menghapus seluruh riwayat analisis (${items.length} data K) untuk dataset "${title}"? Tindakan ini tidak dapat dibatalkan.`,
      onConfirm: async () => {
        setConfirmState(null);
        setIsLoading(true);
        try {
          for (const item of items) {
            await fetch(`${API_BASE_URL}/delete_movie/${item.raw}`, { method: 'DELETE' });
          }
          if (viewedResult && viewedResult.title.replace(/_/g, ' ') === title) {
            setViewedResult(null);
          }
          await fetchSavedMovies();
          showToast(`History "${title}" berhasil dihapus.`, 'success');
        } catch {
          showToast("Gagal menghapus beberapa data.", 'error');
        } finally {
          setIsLoading(false);
        }
      }
    });
  };






  const openFullScreen = () => {
    if (!viewedResult?.vis_html) return;
    const newWindow = window.open('', '_blank');
    if (newWindow) {
      newWindow.document.write(viewedResult.vis_html);
      const distData = viewedResult.overall_distribution;
      const scriptCode = `(function() {
        var dist = ${JSON.stringify(distData)};
        setInterval(function() {
          Object.keys(dist).forEach(function(key) {
            var num    = key.replace('Topik ', '');
            var circle = document.getElementById('topic' + num);
            if (circle) {
              var cx = circle.getAttribute('cx');
              var cy = circle.getAttribute('cy');
              var parent = circle.parentNode;
              if (parent) {
                var texts = parent.querySelectorAll('text');
                texts.forEach(function(t) {
                  if (t.textContent.trim() === String(num) && t.id.indexOf('custom-pct') === -1) {
                    t.style.display = 'none';
                  }
                });
              }
              var customId   = 'custom-pct-' + num;
              var customText = document.getElementById(customId);
              if (!customText) {
                customText = document.createElementNS("http://www.w3.org/2000/svg", "text");
                customText.id = customId;
                customText.setAttribute('text-anchor', 'middle');
                customText.setAttribute('dominant-baseline', 'central');
                customText.setAttribute('fill', '#242424');
                customText.setAttribute('font-size', '16px');
                customText.setAttribute('font-weight', 'bold');
                customText.style.pointerEvents = 'none';
                customText.textContent = dist[key] + '%';
                parent.appendChild(customText);
              }
              if (cx && cy) {
                customText.setAttribute('x', cx);
                customText.setAttribute('y', cy);
              }
            }
          });
        }, 100);
      })();`;
      newWindow.document.write('<script>' + scriptCode + '</script>');
      newWindow.document.close();
    } else {
      showToast("Pop-up diblokir. Mohon izinkan pop-up pada browser Anda.", 'warning');
    }
  };

  let bestCohResult = null, bestPerpResult = null;
  if (viewedResult?.optimal_k_results) {
    const kR = viewedResult.optimal_k_results;
    bestCohResult = kR.reduce((max, c) => c.score > max.score ? c : max, kR[0]);
    bestPerpResult = kR.reduce((min, c) => c.perplexity < min.perplexity ? c : min, kR[0]);
  }

  // [BUG-09] Fungsi potong teks agar tabel distribusi dokumen tetap ringkas
  const truncateText = (text, maxLen = 120) => {
    if (!text) return '';
    return text.length <= maxLen ? text : text.substring(0, maxLen) + '...';
  };

  return (
    <div>
      {/* Confirm Dialog */}
      {confirmState && (
        <ConfirmDialog
          message={confirmState.message}
          onConfirm={confirmState.onConfirm}
          onCancel={() => setConfirmState(null)}
        />
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '15px' }}>
        <h1 className="page-title" style={{ margin: 0 }}>History Analisis</h1>
      </div>

      {Object.keys(groupedMovies).length === 0 ? (
        <div className="card-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <h3 style={{ color: '#242424', margin: '0 0 10px 0', fontSize: '18px' }}>Belum Ada History</h3>
          <p style={{ color: '#717171', fontSize: '14px' }}>
            Hasil pemodelan LDA Anda akan otomatis tersimpan di sini setelah proses analisis selesai.
          </p>
        </div>
      ) : (
        <div className="card-container">
          <div className="scroll-x">
            <table style={{ width: '100%', minWidth: '500px', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ width: '60px', textAlign: 'center' }}>No</th>
                  <th>Judul Dataset</th>
                  <th style={{ textAlign: 'right', width: '200px' }}>Aksi</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(groupedMovies).map(([title, group], i) => {
                  const { items, optimalK } = group;

                  if (!items || items.length === 0) return null;

                  // Pilih item optimal atau item pertama secara otomatis
                  const targetItem = optimalK !== null
                    ? (items.find(it => it.k === optimalK) || items[0])
                    : items[0];

                  return (
                    <tr key={title}>
                      <td style={{ textAlign: 'center', color: '#717171', fontWeight: '600' }}>{i + 1}</td>
                      <td style={{ fontWeight: '700', color: '#161616', fontSize: '14px' }}>{title}</td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                          <button
                            onClick={() => handleLoadHistory(targetItem.raw)}
                            className="btn-browse"
                            style={{ padding: '7px 14px', fontSize: '13px', minWidth: 'auto' }}
                            disabled={isLoading}
                          >
                            Lihat Detail
                          </button>
                          <button
                            onClick={() => handleDeleteGroup(title, items)}
                            className="btn-danger"
                            style={{ padding: '7px 14px', fontSize: '13px' }}
                            disabled={isLoading}
                          >
                            Hapus
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {viewedResult && (
        <div style={{ marginTop: '40px', animation: 'fadeIn 0.5s ease-in-out' }}>

          {/* TAB BAR N-GRAM & K UTAMA PADA DETAIL HISTORY */}
          <div style={{
            backgroundColor: '#ffffff', border: '1px solid #e7e7e7',
            borderRadius: '12px', padding: '18px 22px', marginBottom: '25px',
            boxShadow: '0 1px 3px rgba(15, 23, 42, 0.05)'
          }}>
            {/* Baris 1: Mode N-Gram */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', flexWrap: 'wrap', gap: '10px' }}>
              <h3 style={{ margin: 0, fontSize: '15px', fontWeight: '700', color: '#161616' }}>
                Mode: <span style={{ color: '#5a5a5a', textTransform: 'uppercase' }}>{viewedResult.ngram_mode || 'bigram'}</span>
              </h3>
            </div>

            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
              {[
                { id: 'unigram', label: 'Unigram (1 Kata)' },
                { id: 'bigram', label: 'Bigram (2 Kata)' },
              ].map(tab => {
                const isActive = (viewedResult.ngram_mode || 'bigram') === tab.id;
                const titleStr = viewedResult.title.replace(/_/g, ' ');
                const modeItems = groupedMovies[titleStr]?.items?.filter(it => it.mode === tab.id) || [];
                const targetRaw = modeItems.length > 0 ? modeItems[0].raw : null;

                // Mode dianggap kosong HANYA JIKA SEMUA variasi K-nya tidak memenuhi syarat minimum
                const isEmpty = modeItems.length > 0 ? modeItems.every(it => it.is_empty) : true;
                const isDisabled = !targetRaw || isEmpty;

                let labelSuffix = '';
                if (!targetRaw) labelSuffix = ' (Belum ada)';
                else if (isEmpty) labelSuffix = ' (Tidak ditemukan)';

                return (
                  <button
                    key={tab.id}
                    disabled={isDisabled}
                    onClick={() => targetRaw && !isDisabled && handleLoadHistory(targetRaw)}
                    style={{
                      padding: '7px 16px', fontSize: '13px', fontWeight: '700',
                      borderRadius: '20px', border: '1px solid #d3d3d3', cursor: !isDisabled ? 'pointer' : 'not-allowed',
                      backgroundColor: isActive ? '#111111' : (!isDisabled ? 'var(--bg-app)' : 'var(--bg-subtle)'),
                      color: isActive ? '#ffffff' : (!isDisabled ? 'var(--text-secondary)' : 'var(--text-muted)'),
                      opacity: !isDisabled ? 1 : 0.5,
                      boxShadow: isActive ? '0 2px 4px rgba(0,0,0,0.1)' : 'none',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    {tab.label}{labelSuffix}
                  </button>
                );
              })}
            </div>

            {/* Baris 2: Tab Pilihan Jumlah Topik (K = 2 hingga 10) */}
            {(() => {
              const titleStr = viewedResult.title.replace(/_/g, ' ');
              const currentMode = viewedResult.ngram_mode || 'bigram';
              const groupData = groupedMovies[titleStr];
              const availableItemsForMode = groupData?.items?.filter(it => it.mode === currentMode) || [];

              if (availableItemsForMode.length === 0) return null;

              return (
                <div style={{ paddingTop: '14px', borderTop: '1px solid #f4f4f4' }}>
                  <div style={{ fontSize: '12.5px', fontWeight: '700', color: '#535353', marginBottom: '10px' }}>
                    Pilih Jumlah Topik (K):
                  </div>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {availableItemsForMode.map(item => {
                      const isSelectedK = Number(viewedResult.num_topics) === item.k;
                      const isOptimalK = groupData?.optimalK === item.k;
                      const isDisabledK = item.is_empty;

                      return (
                        <button
                          key={item.raw}
                          disabled={isDisabledK}
                          onClick={() => !isDisabledK && handleLoadHistory(item.raw)}
                          style={{
                            padding: '6px 14px',
                            fontSize: '12.5px',
                            fontWeight: '700',
                            borderRadius: '8px',
                            border: isSelectedK ? '1px solid #111111' : '1px solid var(--border-light)',
                            backgroundColor: isSelectedK ? '#111111' : (isDisabledK ? 'var(--bg-subtle)' : 'var(--bg-app)'),
                            color: isSelectedK ? '#ffffff' : (isDisabledK ? 'var(--text-muted)' : 'var(--text-primary)'),
                            cursor: isDisabledK ? 'not-allowed' : 'pointer',
                            opacity: isDisabledK ? 0.6 : 1,
                            transition: 'all 0.15s ease',
                            boxShadow: isSelectedK ? '0 2px 4px rgba(0,0,0,0.1)' : 'none'
                          }}
                        >
                          K = {item.k} {isOptimalK ? '[Terbaik]' : ''}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })()}
          </div>

          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            marginBottom: '20px', flexWrap: 'wrap', gap: '15px'
          }}>
            <h2 className="section-title" style={{ margin: 0 }}>
              Detail Analisis: {viewedResult.title.replace(/_/g, ' ')}
            </h2>
            <button onClick={() => setViewedResult(null)} className="btn-browse" style={{ fontSize: '13px' }}>
              âœ• Tutup Detail
            </button>
          </div>

          {viewedResult.overall_interpretation && (
            <div style={{ marginTop: '30px', marginBottom: '30px' }}>
              <h2 className="section-title">Interpretasi Umum</h2>
              <div className="card-container" style={{ padding: '22px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-light)', borderLeft: '5px solid var(--accent-blue)', borderRadius: '8px' }}>
                <div 
                  style={{ fontSize: '14.5px', lineHeight: '1.7', color: '#272727', margin: 0, textAlign: 'justify' }}
                  dangerouslySetInnerHTML={{ __html: viewedResult.overall_interpretation.replace(/\\n/g, '<br/>') }}
                />
              </div>
            </div>
          )}

          <AnalysisResultView 
            result={viewedResult} 
            optimalKResults={viewedResult.optimal_k_results} 
            API_BASE_URL={API_BASE_URL} 
            showToast={showToast} 
            onOpenFullScreen={openFullScreen} 
            onInterpretationSaved={(topicName, label, notes) => {
              setViewedResult(prev => {
                if (!prev) return prev;
                return {
                  ...prev,
                  interpretations: {
                    ...(prev.interpretations || {}),
                    [topicName]: { custom_label: label, notes: notes }
                  }
                };
              });
            }}
          />

        </div>
      )}
    </div>
  );
}

export default History;


import { AppContext } from '../context/AppContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function Analysis() {
  const {
    API_BASE_URL, prepSteps, status, setStatus,
    movieTitle, setMovieTitle, numTopics, setNumTopics,
    analysisResult, setAnalysisResult,
    optimalKResults, setOptimalKResults,
    isSearchingK, setIsSearchingK,
    uploadedFilename,
    showToast,
  } = useContext(AppContext);

  const [suggestedK, setSuggestedK] = useState(null);
  const [bestPerplexityK, setBestPerplexityK] = useState(null);
  const [interpretations, setInterpretations] = useState({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [kProgress, setKProgress] = useState({ current: 0, total: 9, currentK: 2 });
  // State untuk fitur edit interpretasi per topik
  const [editingTopic, setEditingTopic] = useState(null);
  const [editBuffer, setEditBuffer] = useState({ label: '', notes: '' });
  const [isSaving, setIsSaving] = useState(false);
  // [REVISI] Tab filter mode N-Gram (Unigram, Bigram, Trigram)
  const [selectedModeTab, setSelectedModeTab] = useState('all');
  // [REVISI UX] Tab tampilan utama vs detail teknis (Awam vs Teknis)
  const [activeTab, setActiveTab] = useState('main');

  const pollRef = useRef(null);

  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  useEffect(() => {
    if (analysisResult?.topics) {
      const saved = analysisResult.interpretations || {};
      const initial = {};
      Object.entries(analysisResult.topics).forEach(([topicName, topicData]) => {
        initial[topicName] = saved[topicName] || {
          custom_label: topicData.auto_label || '',
          notes: topicData.auto_notes || ''
        };
      });
      setInterpretations(initial);
    } else {
      setInterpretations({});
    }
  }, [analysisResult]);

  const openFullScreen = () => {
    if (!analysisResult?.vis_html) return;
    const newWindow = window.open('', '_blank');
    if (newWindow) {
      newWindow.document.write(analysisResult.vis_html);
      const distData = analysisResult.overall_distribution;
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
      newWindow.document.write('<script>' + scriptCode + '<\/script>');
      newWindow.document.close();
    } else {
      showToast("Pop-up diblokir. Mohon izinkan pop-up pada browser Anda.", 'warning');
    }
  };

  // [BUG-01] Simpan interpretasi manual ke backend
  const saveInterpretation = async (topicName) => {
    setIsSaving(true);
    try {
      const res = await fetch(`${API_BASE_URL}/update_interpretation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title:        analysisResult.title,
          num_topics:   analysisResult.num_topics,
          mode:         analysisResult.ngram_mode || 'bigram',
          topic_id:     topicName,
          custom_label: editBuffer.label,
          notes:        editBuffer.notes,
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setInterpretations(prev => ({
          ...prev,
          [topicName]: { custom_label: editBuffer.label, notes: editBuffer.notes }
        }));
        setEditingTopic(null);
        showToast(`Label “${topicName}” berhasil disimpan!`, 'success');
      } else {
        showToast(data.error || 'Gagal menyimpan interpretasi.', 'error');
      }
    } catch {
      showToast('Tidak dapat terhubung ke server.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  // [BUG-08] Potong teks ulasan agar tabel distribusi dokumen tetap ringkas
  const truncateText = (text, maxLen = 120) => {
    if (!text) return '';
    return text.length <= maxLen ? text : text.substring(0, maxLen) + '...';
  };

  // Memuat model spesifik berdasarkan mode N-Gram dan K
  const loadSpecificModel = async (targetMode, targetK) => {
    if (!movieTitle || !movieTitle.trim()) return;
    const cleanTitle = movieTitle.trim().replace(/\s+/g, '_');
    const dbKey = `${cleanTitle}_${targetMode}_k${targetK}`;
    setIsAnalyzing(true);
    try {
      const res = await fetch(`${API_BASE_URL}/saved_movies/${dbKey}`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'success' && data.data) {
          setAnalysisResult(data.data);
          setNumTopics(targetK);
          showToast(`Menampilkan hasil N-Gram: ${targetMode.toUpperCase()} (K=${targetK})`, 'info');
          setIsAnalyzing(false);
          return;
        }
      }
      // Fallback jika belum di-cache: jalankan /analyze
      await runAnalyze(targetK, targetMode, optimalKResults);
    } catch {
      showToast('Gagal memuat model untuk mode N-Gram ini.', 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Switch N-Gram Tab secara penuh (100% memisahkan seluruh hasil)
  const handleSwitchNgramMode = async (mode) => {
    setSelectedModeTab(mode);
    if (!optimalKResults) return;

    // Cari K terbaik untuk mode N-Gram ini (berdasarkan Coherence score)
    const modeItems = optimalKResults.filter(item => item.mode === mode);
    if (modeItems.length > 0) {
      const bestItem = modeItems.reduce((max, curr) => curr.score > max.score ? curr : max, modeItems[0]);
      await loadSpecificModel(mode, bestItem.k);
    }
  };

  // Jalankan LDA setelah K diketahui 
  const runAnalyze = async (bestK, bestMode, kResults) => {
    setIsAnalyzing(true);
    setStatus(`Melatih model LDA final dengan K=${bestK} (${bestMode})...`);
    setAnalysisResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: movieTitle.trim(),
          num_topics: bestK,
          mode: bestMode,
          filename: uploadedFilename,
          optimal_k_results: kResults
        })
      });
      if (!response.ok) {
        let errStr = `Error ${response.status}`;
        try { const e = await response.json(); errStr = e.error || errStr; } catch (_) { }
        setStatus(`Gagal Analisis: ${errStr}`);
        showToast(errStr, 'error');
        return;
      }
      const data = await response.json();
      if (data.status === 'success') {
        setAnalysisResult(data.data);
        setNumTopics(bestK);
        setStatus(`Selesai! Model LDA K=${bestK} (${bestMode}) berhasil dibangun.`);
        showToast(`Analisis LDA selesai dengan K=${bestK} (${bestMode})!`, 'success');
      } else {
        setStatus(`Gagal Analisis: ${data.error}`);
        showToast(data.error, 'error');
      }
    } catch {
      setStatus("Gagal menghubungi server backend.");
      showToast("Tidak dapat terhubung ke server.", 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  //Cari K → Analisis otomatis
  const handleFullAnalysis = async () => {
    if (!prepSteps) {
      showToast("Lakukan preprocessing terlebih dahulu.", 'warning');
      return;
    }
    if (!movieTitle || !movieTitle.trim()) {
      showToast("Isi Nama / Judul Dataset terlebih dahulu.", 'warning');
      return;
    }

    // Reset state
    setIsSearchingK(true);
    setOptimalKResults(null);
    setSuggestedK(null);
    setBestPerplexityK(null);
    setAnalysisResult(null);
    setKProgress({ current: 0, total: 27, currentK: 2 });
    setStatus("Memulai evaluasi Topik 2 sampai 10 (semua K)...");

    try {
      // Langkah 1: Mulai background task cari K optimal
      const startRes = await fetch(`${API_BASE_URL}/find_optimal_k`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          min_k: 2, max_k: 10,
          filename: uploadedFilename,
          title: movieTitle.trim()
        })
      });

      const startData = await startRes.json();
      if (startData.status !== 'started') {
        showToast(startData.error || 'Gagal memulai kalkulasi.', 'error');
        setIsSearchingK(false);
        return;
      }

      const taskId = startData.task_id;

      // Langkah 2: Polling hingga selesai
      pollRef.current = setInterval(async () => {
        try {
          const statusRes = await fetch(`${API_BASE_URL}/task_status/${taskId}`);
          const statusData = await statusRes.json();

          if (!statusData.data) {
            clearInterval(pollRef.current);
            setIsSearchingK(false);
            showToast('Gagal membaca status task.', 'error');
            return;
          }

          const task = statusData.data;

          if (task.status === 'running') {
            const done = task.progress + 1;
            setKProgress({ current: done, total: task.total, currentK: task.current_k });
            setStatus(`Mengevaluasi ${task.current_mode} K=${task.current_k} (${done}/${task.total})...`);

          } else if (task.status === 'done') {
            clearInterval(pollRef.current);
            setIsSearchingK(false);

            const results = task.result;
            const bestCoh = results.reduce((max, c) => c.score > max.score ? c : max, results[0]);
            const bestPerp = results.reduce((min, c) => c.perplexity < min.perplexity ? c : min, results[0]);

            setOptimalKResults(results);
            setSuggestedK(bestCoh);
            setBestPerplexityK(bestPerp);
            setSelectedModeTab(bestCoh.mode || 'bigram');
            setStatus(`Evaluasi selesai. Mode K optimal: ${bestCoh.k} (${bestCoh.mode}). Memuat hasil penuh...`);
            showToast(`Evaluasi selesai! Menampilkan mode ${bestCoh.mode.toUpperCase()} (K=${bestCoh.k})...`, 'success');

            // Langkah 3: Langsung tampilkan hasil analisis LDA lengkap untuk mode terbaik
            await runAnalyze(bestCoh.k, bestCoh.mode, results);

          } else if (task.status === 'error') {
            clearInterval(pollRef.current);
            setIsSearchingK(false);
            setStatus(`Gagal: ${task.error}`);
            showToast(`Gagal kalkulasi: ${task.error}`, 'error');
          }
        } catch {
          clearInterval(pollRef.current);
          setIsSearchingK(false);
          showToast('Gagal menghubungi server saat polling.', 'error');
        }
      }, 2000);

    } catch {
      setIsSearchingK(false);
      showToast('Gagal menghubungi server.', 'error');
    }
  };

  const isBusy = isSearchingK || isAnalyzing;
  const progressPct = kProgress.total > 0
    ? Math.round((kProgress.current / kProgress.total) * 100)
    : 0;

  // Label tombol sesuai fase
  const btnLabel = isSearchingK
    ? `Mengevaluasi K=${kProgress.currentK} (${kProgress.current}/${kProgress.total})…`
    : isAnalyzing
      ? 'Melatih Model LDA Final…'
      : 'Jalankan Analisis';

  return (
    <div>
      <h1 className="page-title">Analisis Topik (LDA)</h1>

      {(!prepSteps && !analysisResult) ? (
        <div className="card-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <h3 style={{ color: '#242424', margin: '0 0 10px 0', fontSize: '18px' }}>Data Belum Siap</h3>
          <p className="text-muted" style={{ marginBottom: '25px' }}>
            Anda harus menyelesaikan tahapan Preprocessing terlebih dahulu sebelum dapat membangun model LDA.
          </p>
        </div>
      ) : (
        <div>
          {/* ── Panel Konfigurasi & Progress ── */}
          <div className="card-container">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

              {/* Konfigurasi */}
              <div style={{ width: '100%' }}>
                <h3 className="card-title">Konfigurasi Model</h3>
                <div style={{ marginBottom: '15px' }}>
                  <input
                    type="text"
                    value={movieTitle}
                    onChange={(e) => setMovieTitle(e.target.value)}
                    placeholder="Judul Film"
                    style={{
                      width: '100%', padding: '10px', borderRadius: '6px',
                      border: '1px solid #e6e6e6', boxSizing: 'border-box'
                    }}
                  />
                </div>

                <button
                  onClick={handleFullAnalysis}
                  className="btn-primary"
                  style={{ width: '100%', padding: '12px', fontSize: '15px' }}
                  disabled={isBusy}
                >
                  {btnLabel}
                </button>

                <p className="text-muted" style={{ marginTop: '12px', textAlign: 'center', fontSize: '13px' }}>
                  {status}
                </p>
              </div>

              {/* Progress & Hasil Evaluasi K */}
              <div style={{
                width: '100%', backgroundColor: '#f9f9f9', padding: '20px',
                borderRadius: '8px', border: '1px solid #e6e6e6'
              }}>
                <h3 className="card-title">Evaluasi Model (Coherence &amp; Perplexity)</h3>

                {/* Progress bar saat evaluasi berjalan */}
                {isSearchingK && (
                  <div className="progress-wrapper">
                    <p className="progress-label">
                      Mengevaluasi K={kProgress.currentK}&nbsp;
                      <span style={{ color: '#717171', fontWeight: 'normal' }}>
                        ({kProgress.current}/{kProgress.total} selesai)
                      </span>
                    </p>
                    <div className="progress-bar-track">
                      <div className="progress-bar-fill" style={{ width: `${progressPct}%` }} />
                    </div>
                    <p style={{ margin: '6px 0 0 0', fontSize: '12px', color: '#a2a2a2', textAlign: 'right' }}>
                      {progressPct}%
                    </p>
                  </div>
                )}

                {/* Indikator fase analisis */}
                {isAnalyzing && (
                  <div style={{
                    padding: '12px 16px', backgroundColor: '#f4f4f4',
                    borderRadius: '8px', border: '1px solid #d6d6d6', marginBottom: '16px'
                  }}>
                    <p style={{ margin: 0, fontSize: '13px', color: '#4f4f4f', fontWeight: '600' }}>
                      Melatih model LDA final dengan K={numTopics}...
                    </p>
                  </div>
                )}

                {/* Tabel & Grafik hasil evaluasi */}
                {optimalKResults && (
                  <div style={{ animation: 'fadeIn 0.5s ease-in-out' }}>

                    {/* KOTAK PENJELASAN AWAM (GLOSSARY) */}
                    <div style={{
                      backgroundColor: '#f9f9f9', border: '1px solid #e7e7e7',
                      borderRadius: '8px', padding: '12px 15px', marginBottom: '15px'
                    }}>
                      <p style={{ margin: '0 0 6px 0', fontSize: '13px', fontWeight: '700', color: '#3f3f3f' }}>
                        Panduan Membaca Evaluasi Model:
                      </p>
                      <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', color: '#535353', lineHeight: '1.5' }}>
                        <li><strong>Unigram (1 Kata)</strong>: Analisis berdasarkan kata per kata tunggal (misal: "bagus", "alur").</li>
                        <li><strong>Bigram (2 Kata)</strong>: Analisis pasangan 2 kata berdampingan (misal: "efek_visual", "alur_cerita").</li>
                        <li><strong>Trigram (3 Kata)</strong>: Analisis frasa 3 kata berdampingan (misal: "sangat_bagus_sekali").</li>
                        <li><strong>Coherence (Tingkat Kejelasan Topik)</strong>: <em>Semakin tinggi nilainya, semakin fokus dan mudah dipahami topik tersebut.</em></li>
                        <li><strong>Perplexity (Tingkat Kebingungan)</strong>: <em>Semakin rendah nilainya, semakin baik model memahami ulasan.</em></li>
                      </ul>
                    </div>

                    {/* TAB NAVIGASI PILIHAN N-GRAM — TABEL & GRAFIK TERPISAH PER MODE */}
                    <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
                      <span style={{ fontSize: '12.5px', fontWeight: '700', color: '#535353' }}>Mode:</span>
                      {[
                        { id: 'unigram', label: 'Unigram (1 Kata)' },
                        { id: 'bigram', label: 'Bigram (2 Kata)' },
                        { id: 'trigram', label: 'Trigram (3 Kata)' },
                      ].map(tab => (
                        <button
                          key={tab.id}
                          onClick={() => handleSwitchNgramMode(tab.id)}
                          style={{
                            padding: '7px 16px', fontSize: '13px', fontWeight: '700',
                            borderRadius: '20px', border: '1px solid #d3d3d3', cursor: 'pointer',
                            backgroundColor: selectedModeTab === tab.id ? '#272727' : '#f9f9f9',
                            color: selectedModeTab === tab.id ? '#ffffff' : '#535353',
                            boxShadow: selectedModeTab === tab.id ? '0 2px 8px rgba(0,0,0,0.15)' : 'none',
                            transition: 'all 0.2s'
                          }}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>

                    <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: '700', color: '#161616' }}>
                      Tabel & Grafik Evaluasi — Mode <span style={{ color: '#5a5a5a', textTransform: 'uppercase' }}>{selectedModeTab !== 'all' ? selectedModeTab : (analysisResult?.ngram_mode || 'bigram')}</span>
                      <span style={{ fontSize: '12px', fontWeight: 'normal', color: '#717171', marginLeft: '10px' }}>
                        (Klik salah satu baris untuk memuat hasil K tersebut)
                      </span>
                    </h4>

                    {(() => {
                      // Selalu filter berdasarkan mode aktif (tidak ada "Semua Mode" lagi)
                      const activeMode = selectedModeTab !== 'all'
                        ? selectedModeTab
                        : (analysisResult?.ngram_mode || 'bigram');
                      const displayList = optimalKResults.filter(item => item.mode === activeMode);

                      return (
                        <>
                          <div style={{
                            maxHeight: '200px', overflowY: 'auto', border: '1px solid #e6e6e6',
                            borderRadius: '6px', marginBottom: '20px'
                          }}>
                            <table style={{
                              width: '100%', fontSize: '12px', backgroundColor: '#ffffff',
                              borderCollapse: 'collapse', marginTop: 0
                            }}>
                              <thead style={{ position: 'sticky', top: 0, backgroundColor: '#f3f3f3', zIndex: 1 }}>
                                <tr>
                                  <th style={{ padding: '8px', textAlign: 'center', borderBottom: '1px solid #e6e6e6' }}>Jumlah Topik (K)</th>
                                  <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #e6e6e6' }}>Coherence (Kejelasan Topik)</th>
                                  <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #e6e6e6' }}>Perplexity (Kebingungan Model)</th>
                                </tr>
                              </thead>
                              <tbody>
                                 {displayList.length === 0 ? (
                                  <tr>
                                      Belum ada data evaluasi untuk mode <strong style={{ textTransform: 'uppercase' }}>{activeMode}</strong>.
                                    </td>
                                  </tr>
                                ) : (() => {
                                  // Hitung best coherence & best perplexity dari displayList (per mode aktif)
                                  const bestCohInList  = displayList.reduce((best, r) => r.score > best.score ? r : best, displayList[0]);
                                  const bestPerpInList = displayList.reduce((best, r) => r.perplexity < best.perplexity ? r : best, displayList[0]);

                                  return displayList.map((res, i) => {
                                    const isBestCoh      = res.k === bestCohInList.k;
                                    const isBestPerp     = res.k === bestPerpInList.k;
                                    const isCurrentActive = analysisResult?.num_topics === res.k && analysisResult?.ngram_mode === res.mode;
                                    return (
                                      <tr
                                        key={i}
                                        onClick={() => loadSpecificModel(res.mode, res.k)}
                                        title="Klik untuk memuat hasil analisis K ini"
                                        style={{
                                          backgroundColor: isCurrentActive ? '#e0e7ff' : (isBestCoh ? '#fefce8' : 'transparent'),
                                          cursor: 'pointer',
                                          borderLeft: isBestCoh ? '3px solid #f59e0b' : '3px solid transparent',
                                        }}
                                      >
                                        <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'center', fontWeight: 'bold' }}>
                                          K = {res.k}
                                          {isCurrentActive && <span style={{ color: '#4f46e5', fontSize: '11px', marginLeft: '5px' }}>✓ Aktif</span>}
                                          {isBestCoh && <span style={{ color: '#d97706', fontSize: '11px', marginLeft: '5px' }}>⭐ Terbaik</span>}
                                        </td>
                                        <td style={{
                                          padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right',
                                          color: isBestCoh ? '#b45309' : '#4b5563',
                                          fontWeight: isBestCoh ? '700' : 'normal'
                                        }}>
                                          {res.score.toFixed(4)}
                                        </td>
                                        <td style={{
                                          padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right',
                                          color: isBestPerp ? '#059669' : '#4b5563',
                                          fontWeight: isBestPerp ? '700' : 'normal'
                                          fontWeight: isBestPerp ? '700' : 'normal'
                                        }}>
                                          {res.perplexity.toFixed(4)}
                                          {isBestPerp && <span style={{ color: '#059669', fontSize: '11px', marginLeft: '4px', fontWeight: '600' }}>[Terbaik]</span>}
                                        </td>
                                      </tr>
                                    );
                                  });
                                })()}
                              </tbody>
                            </table>
                          </div>

                          <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#4b5563' }}>Grafik Perbandingan</h4>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '15px' }}>
                            {[
                              { dataKey: 'score', name: 'Coherence', color: '#3b82f6', label: '📈 Coherence Score (Semakin Tinggi = Lebih Jelas Disarankan)', tColor: '#1d4ed8' },
                              { dataKey: 'perplexity', name: 'Perplexity', color: '#10b981', label: '📉 Perplexity Score (Semakin Rendah = Lebih Baik)', tColor: '#047857' },
                            ].map(({ dataKey, name, color, label, tColor }) => (
                              <div key={dataKey} style={{
                                width: '100%', height: '220px', backgroundColor: '#fff',
                                padding: '15px 10px 10px', borderRadius: '8px', border: '1px solid #e5e7eb'
                              }}>
                                <h5 style={{ margin: '0 0 15px 0', fontSize: '12px', color: tColor, textAlign: 'center' }}>{label}</h5>
                                <ResponsiveContainer width="100%" height="80%">
                                  <LineChart data={displayList} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                                    <XAxis dataKey="k" tick={{ fontSize: 11 }} />
                                    <YAxis tick={{ fontSize: 11, fill: color }} axisLine={false} tickLine={false} domain={['auto', 'auto']} />
                                    <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
                                    <Line type="monotone" dataKey={dataKey} name={name} stroke={color} strokeWidth={2} activeDot={{ r: 6 }} />
                                  </LineChart>
                                </ResponsiveContainer>
                              </div>
                            ))}
                          </div>
                        </>
                      );
                    })()}

                    {/* Kartu Terbaik per Mode berdasarkan Coherence */}
                        { id: 'unigram', label: 'Unigram (1 Kata)', emoji: '🔤', bg: '#eff6ff', border: '#bfdbfe', textColor: '#1e3a8a', accent: '#2563eb', badgeBg: '#dbeafe' },
                        { id: 'bigram',  label: 'Bigram (2 Kata)',  emoji: '🔗', bg: '#f5f3ff', border: '#c4b5fd', textColor: '#3b0764', accent: '#7c3aed', badgeBg: '#ede9fe' },
                        { id: 'trigram', label: 'Trigram (3 Kata)', emoji: '📜', bg: '#ecfdf5', border: '#a7f3d0', textColor: '#065f46', accent: '#059669', badgeBg: '#d1fae5' },
                      ];
                      // Cari K terbaik (coherence tertinggi) per mode
                      const bestPerMode = modeConfig.map(mc => {
                        const items = optimalKResults.filter(r => r.mode === mc.id);
                        const best  = items.length > 0 ? items.reduce((a, b) => b.score > a.score ? b : a, items[0]) : null;
                        return { ...mc, best };
                      });
                      // Mode mana yang paling unggul secara keseluruhan (coherence tertinggi di antara semua best)
                      const overallWinner = bestPerMode.reduce((w, m) =>
                        m.best && (!w.best || m.best.score > w.best.score) ? m : w, bestPerMode[0]);

                      return (
                        <div>
                          <p style={{ margin: '0 0 10px 0', fontSize: '12.5px', fontWeight: '700', color: '#475569' }}>
                            K Terbaik per Mode (Berdasarkan Coherence)
                          </p>
                          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                            {bestPerMode.map(mc => {
                              const isWinner = mc.id === overallWinner.id;
                              const isActive = selectedModeTab === mc.id;
                              return (
                                <div
                                  key={mc.id}
                                  onClick={() => mc.best && handleSwitchNgramMode(mc.id)}
                                  title={mc.best ? `Klik untuk beralih ke mode ${mc.label} (K=${mc.best.k})` : 'Belum ada data'}
                                  style={{
                                    flex: '1 1 calc(33% - 10px)', minWidth: '130px',
                                    backgroundColor: mc.bg, padding: '12px 14px',
                                    borderRadius: '8px', cursor: mc.best ? 'pointer' : 'default',
                                    border: `2px solid ${isActive ? mc.accent : isWinner ? mc.accent : mc.border}`,
                                    boxShadow: isActive ? `0 0 0 3px ${mc.accent}33` : isWinner ? `0 2px 8px ${mc.accent}30` : 'none',
                                    transition: 'all 0.2s', position: 'relative'
                                  }}
                                >
                                  {/* Badge terbaik keseluruhan */}
                                  {isWinner && (
                                    <span style={{
                                      position: 'absolute', top: '-8px', right: '10px',
                                      backgroundColor: '#f59e0b', color: '#fff',
                                      fontSize: '10px', fontWeight: '700',
                                      padding: '2px 8px', borderRadius: '10px',
                                      padding: '2px 8px', borderRadius: '10px',
                                      boxShadow: '0 1px 4px rgba(0,0,0,0.2)'
                                    }}>
                                      TERBAIK
                                    </span>
                                  )}
                                  <p style={{ margin: '0 0 5px 0', fontSize: '11.5px', fontWeight: '700', color: mc.accent }}>
                                    {mc.label}
                                  </p>
                                  {mc.best ? (
                                    <>
                                      <p style={{ margin: '0 0 3px 0', fontSize: '18px', fontWeight: '800', color: mc.textColor }}>
                                        K = {mc.best.k}
                                      </p>
                                      <p style={{ margin: 0, fontSize: '11px', color: mc.accent, fontWeight: '600' }}>
                                        Coherence: {mc.best.score.toFixed(4)}
                                      </p>
                                    </>
                                  ) : (
                                    <p style={{ margin: 0, fontSize: '12px', color: '#a2a2a2' }}>Belum ada data</p>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                )}

                {/* Placeholder saat belum ada data */}
                {!optimalKResults && !isSearchingK && !isAnalyzing && (
                  <p className="text-muted" style={{ textAlign: 'center', padding: '30px 0' }}>
                    Klik tombol <strong>Jalankan Analisis</strong> untuk memulai.
                  </p>
                )}
              </div>
            </div>
          </div>


      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '15px' }}>
        <h1 style={{ fontSize: '24px', margin: 0, color: '#272727' }}>Analisis Topik (LDA)</h1>
        {analysisResult && (
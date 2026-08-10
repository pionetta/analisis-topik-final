import { useContext, useState, useEffect, useRef } from 'react';
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

  //Jalankan LDA setelah K diketahui 
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
        setStatus(`Selesai! Model LDA K=${bestK} berhasil dibangun.`);
        showToast(`Analisis LDA selesai dengan K=${bestK}!`, 'success');
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
    setKProgress({ current: 0, total: 9, currentK: 2 });
    setStatus("Memulai evaluasi Topik 2 sampai 10");

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
            setStatus(`Evaluasi selesai. K optimal (Coherence): ${bestCoh.k} (${bestCoh.mode}). Melatih model final...`);
            showToast(`Evaluasi K selesai! Melanjutkan analisis dengan K=${bestCoh.k} (${bestCoh.mode})...`, 'info');

            // Langkah 3: Langsung jalankan analisis dengan K terbaik
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
          <div style={{ fontSize: '40px', marginBottom: '15px' }}>⚙️</div>
          <h3 style={{ color: '#242424', margin: '0 0 10px 0', fontSize: '18px' }}>Data Belum Siap</h3>
          <p className="text-muted" style={{ marginBottom: '25px' }}>
            Anda harus menyelesaikan tahapan Preprocessing terlebih dahulu sebelum dapat membangun model LDA.
          </p>
        </div>
      ) : (
        <>
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
                      border: '1px solid #e5e7eb', boxSizing: 'border-box'
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
                width: '100%', backgroundColor: '#f9fafb', padding: '20px',
                borderRadius: '8px', border: '1px solid #e5e7eb'
              }}>
                <h3 className="card-title">Evaluasi Model (Coherence &amp; Perplexity)</h3>

                {/* Progress bar saat evaluasi berjalan */}
                {isSearchingK && (
                  <div className="progress-wrapper">
                    <p className="progress-label">
                      Mengevaluasi K={kProgress.currentK}&nbsp;
                      <span style={{ color: '#6b7280', fontWeight: 'normal' }}>
                        ({kProgress.current}/{kProgress.total} selesai)
                      </span>
                    </p>
                    <div className="progress-bar-track">
                      <div className="progress-bar-fill" style={{ width: `${progressPct}%` }} />
                    </div>
                    <p style={{ margin: '6px 0 0 0', fontSize: '12px', color: '#9ca3af', textAlign: 'right' }}>
                      {progressPct}%
                    </p>
                  </div>
                )}

                {/* Indikator fase analisis */}
                {isAnalyzing && (
                  <div style={{
                    padding: '12px 16px', backgroundColor: '#eff6ff',
                    borderRadius: '8px', border: '1px solid #bfdbfe', marginBottom: '16px'
                  }}>
                    <p style={{ margin: 0, fontSize: '13px', color: '#1d4ed8', fontWeight: '600' }}>
                      Melatih model LDA final dengan K={numTopics}...
                    </p>
                  </div>
                )}

                {/* Tabel & Grafik hasil evaluasi */}
                {optimalKResults && (
                  <div style={{ animation: 'fadeIn 0.5s ease-in-out' }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#4b5563' }}>Tabel Hasil Kalkulasi</h4>
                    <div style={{
                      maxHeight: '180px', overflowY: 'auto', border: '1px solid #e5e7eb',
                      borderRadius: '6px', marginBottom: '20px'
                    }}>
                      <table style={{
                        width: '100%', fontSize: '12px', backgroundColor: '#fff',
                        borderCollapse: 'collapse', marginTop: 0
                      }}>
                        <thead style={{ position: 'sticky', top: 0, backgroundColor: '#f3f4f6', zIndex: 1 }}>
                          <tr>
                            <th style={{ padding: '8px', textAlign: 'center', borderBottom: '1px solid #e5e7eb' }}>K</th>
                            <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Coherence Score</th>
                            <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }}>Perplexity Score</th>
                          </tr>
                        </thead>
                        <tbody>
                          {optimalKResults.map((res, i) => {
                            const isBestCoh = suggestedK?.k === res.k;
                            const isBestPerp = bestPerplexityK?.k === res.k;
                            return (
                              <tr key={i} style={{ backgroundColor: (isBestCoh || isBestPerp) ? '#eff6ff' : 'transparent' }}>
                                <td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'center', fontWeight: 'bold' }}>{res.k}</td>
                                <td style={{
                                  padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right',
                                  color: isBestCoh ? '#2563eb' : '#4b5563', fontWeight: isBestCoh ? 'bold' : 'normal'
                                }}>
                                  {res.score.toFixed(4)} {isBestCoh && '⭐'}
                                </td>
                                <td style={{
                                  padding: '8px', borderBottom: '1px solid #f3f4f6', textAlign: 'right',
                                  color: isBestPerp ? '#059669' : '#4b5563', fontWeight: isBestPerp ? 'bold' : 'normal'
                                }}>
                                  {res.perplexity.toFixed(4)} {isBestPerp && '⭐'}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>

                    <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#4b5563' }}>Grafik Perbandingan</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '15px' }}>
                      {[
                        { dataKey: 'score', name: 'Coherence', color: '#3b82f6', label: '📈 Coherence (Makin Tinggi = Baik)', tColor: '#1d4ed8' },
                        { dataKey: 'perplexity', name: 'Perplexity', color: '#10b981', label: '📉 Perplexity (Makin Rendah = Baik)', tColor: '#047857' },
                      ].map(({ dataKey, name, color, label, tColor }) => (
                        <div key={dataKey} style={{
                          width: '100%', height: '220px', backgroundColor: '#fff',
                          padding: '15px 10px 10px', borderRadius: '8px', border: '1px solid #e5e7eb'
                        }}>
                          <h5 style={{ margin: '0 0 15px 0', fontSize: '12px', color: tColor, textAlign: 'center' }}>{label}</h5>
                          <ResponsiveContainer width="100%" height="80%">
                            <LineChart data={optimalKResults} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
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

                    <div style={{ display: 'flex', gap: '15px' }}>
                      <div style={{ flex: 1, backgroundColor: '#eff6ff', padding: '12px', borderRadius: '6px', border: '1px solid #bfdbfe' }}>
                        <p style={{ margin: '0 0 5px 0', fontSize: '12px', color: '#1d4ed8', fontWeight: '600' }}> Coherence Tertinggi</p>
                        <h3 style={{ margin: 0, color: '#1e3a8a', fontSize: '18px' }}>K = {suggestedK?.k}</h3>
                        <p style={{ margin: 0, fontSize: '12px', color: '#3b82f6' }}>Score: {suggestedK?.score.toFixed(4)}</p>
                      </div>
                      <div style={{ flex: 1, backgroundColor: '#ecfdf5', padding: '12px', borderRadius: '6px', border: '1px solid #a7f3d0' }}>
                        <p style={{ margin: '0 0 5px 0', fontSize: '12px', color: '#047857', fontWeight: '600' }}>Perplexity Terendah</p>
                        <h3 style={{ margin: 0, color: '#065f46', fontSize: '18px' }}>K = {bestPerplexityK?.k}</h3>
                        <p style={{ margin: 0, fontSize: '12px', color: '#10b981' }}>Score: {bestPerplexityK?.perplexity.toFixed(4)}</p>
                      </div>
                    </div>
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

          {/* ── Hasil Analisis LDA ── */}
          {analysisResult && (
            <div style={{ marginTop: '25px', animation: 'fadeIn 0.5s ease-in-out' }}>

              <div className="card-container" style={{
                display: 'flex', justifyContent: 'space-between',
                alignItems: 'center', backgroundColor: '#242424', color: '#fff'
              }}>
                <div>
                  <h3 style={{ margin: '0 0 5px 0', color: '#fff' }}>Ringkasan Model</h3>
                  <p style={{ margin: 0, fontSize: '13px', color: '#9ca3af' }}>
                    Judul: {analysisResult.title} &bull; K: {analysisResult.num_topics}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '30px', textAlign: 'right' }}>
                  <div>
                    <p style={{ margin: '0 0 5px 0', fontSize: '13px', color: '#9ca3af' }}>Perplexity Score</p>
                    <h2 style={{ margin: 0, color: '#10b981' }}>{analysisResult.perplexity_score || '-'}</h2>
                  </div>
                  <div title="Semakin tinggi nilainya, semakin jelas dan mudah dipahami kata-kata dalam topik tersebut.">
                    <p style={{ margin: '0 0 5px 0', fontSize: '13px', color: '#9ca3af', cursor: 'help' }}>Tingkat Kejelasan Topik ℹ️</p>
                    <h2 style={{ margin: 0, color: '#3b82f6' }}>{analysisResult.coherence_score}</h2>
                  </div>
                </div>
              </div>

              {/* KESIMPULAN CERDAS OTOMATIS */}
              <div style={{ backgroundColor: '#eff6ff', padding: '15px 20px', borderRadius: '8px', border: '1px solid #bfdbfe', marginBottom: '25px', marginTop: '15px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#1d4ed8', fontSize: '15px' }}>💡 Kesimpulan Otomatis</h4>
                <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6', color: '#1e3a8a' }}>
                  Dari ulasan <strong>{analysisResult.title}</strong>, model menemukan <strong>{analysisResult.num_topics} topik utama</strong> yang dibicarakan penonton. 
                  Topik yang paling dominan dibicarakan adalah mengenai <strong>{
                    Object.entries(analysisResult.overall_distribution).sort((a,b)=>b[1]-a[1])[0]
                      ? (interpretations[Object.entries(analysisResult.overall_distribution).sort((a,b)=>b[1]-a[1])[0][0]]?.custom_label || analysisResult.topics?.[Object.entries(analysisResult.overall_distribution).sort((a,b)=>b[1]-a[1])[0][0]]?.auto_label || "Topik 1")
                      : "Topik"
                  }</strong> (sebanyak {Object.entries(analysisResult.overall_distribution).sort((a,b)=>b[1]-a[1])[0]?.[1] || 0}%).
                  Silakan lihat detail kata-kata kuncinya di bawah ini untuk memahami lebih lanjut.
                </p>
              </div>

              <h2 className="section-title">Persentase Topik Keseluruhan</h2>
              <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginBottom: '30px' }}>
                {Object.entries(analysisResult.overall_distribution).map(([topic, pct], idx) => {
                  const label = interpretations[topic]?.custom_label || analysisResult.topics?.[topic]?.auto_label;
                  return (
                    <div key={idx} className="stat-card">
                      <h4>{label ? `${topic}: ${label}` : topic}</h4>
                      <h2>{pct}%</h2>
                    </div>
                  );
                })}
              </div>

              <h2 className="section-title">Distribusi Kata &amp; Interpretasi</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                {Object.entries(analysisResult.topics).map(([topicName, topicData], i) => (
                  <div key={i} className="card-container" style={{ padding: '20px', marginBottom: 0 }}>
                    <h3 style={{ margin: '0 0 5px 0', fontSize: '16px', color: '#242424' }}>
                      {interpretations[topicName]?.custom_label
                        ? `${topicName}: ${interpretations[topicName].custom_label}`
                        : topicName}
                    </h3>
                    <table style={{ width: '100%', marginTop: '10px', marginBottom: '20px', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ padding: '8px 0', fontSize: '12px', textAlign: 'left', borderBottom: '1px solid #e5e7eb' }}>Kata</th>
                          <th style={{ padding: '8px 0', fontSize: '12px', textAlign: 'right', borderBottom: '1px solid #e5e7eb' }} title="Seberapa kuat kata ini mewakili keseluruhan topik.">Kekuatan Kata ℹ️</th>
                        </tr>
                      </thead>
                      <tbody>
                        {topicData.words.slice(0, 7).map((w, idx) => (
                          <tr key={idx}>
                            <td style={{ padding: '6px 0', fontSize: '14px', borderBottom: '1px solid #f9fafb' }}>{w.word}</td>
                            <td style={{
                              padding: '6px 0', fontSize: '14px', borderBottom: '1px solid #f9fafb',
                              textAlign: 'right', color: '#6b7280'
                            }}>
                              {w.weight.toFixed(4)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <div style={{
                      borderTop: '1px solid #e5e7eb', backgroundColor: '#f9fafb',
                      margin: '0 -20px -20px -20px', padding: '15px 20px 20px 20px',
                      borderBottomLeftRadius: '12px', borderBottomRightRadius: '12px'
                    }}>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '13px', color: '#242424' }}>Catatan Analisis</h4>
                      <div style={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '4px', padding: '10px 12px' }}>
                        <p className="text-muted" style={{ margin: 0, lineHeight: '1.6' }}>
                          {interpretations[topicName]?.notes || "Belum ada catatan analisis."}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {analysisResult.document_distributions && (
                <>
                  <h2 className="section-title">Klasifikasi Topik pada Dokumen Ulasan</h2>
                  <div className="card-container" style={{ padding: 0, overflow: 'hidden' }}>
                    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 0 }}>
                        <thead style={{ position: 'sticky', top: 0, backgroundColor: '#f9fafb', zIndex: 1 }}>
                          <tr>
                            <th style={{ padding: '12px 15px', textAlign: 'center', borderBottom: '1px solid #e5e7eb', fontSize: '13px', color: '#4b5563' }}>ID</th>
                            <th style={{ padding: '12px 15px', textAlign: 'left', borderBottom: '1px solid #e5e7eb', fontSize: '13px', color: '#4b5563' }}>Cuplikan Teks Ulasan</th>
                            <th style={{ padding: '12px 15px', textAlign: 'center', borderBottom: '1px solid #e5e7eb', fontSize: '13px', color: '#4b5563' }}>Topik Dominan</th>
                          </tr>
                        </thead>
                        <tbody>
                          {analysisResult.document_distributions.slice(0, 50).map((doc, idx) => {
                            const dom = doc.dominant_topic;
                            const lbl = interpretations[dom]?.custom_label || analysisResult.topics?.[dom]?.auto_label;
                            const display = lbl ? `${dom}: ${lbl}` : dom;
                            return (
                              <tr key={idx} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                <td style={{ padding: '12px 15px', textAlign: 'center', color: '#9ca3af', fontSize: '13px' }}>{doc.doc_id}</td>
                                <td style={{ padding: '12px 15px', color: '#4b5563', fontSize: '13px', lineHeight: '1.5' }}>{doc.text}</td>
                                <td style={{ padding: '12px 15px', textAlign: 'center' }}>
                                  <span className="topic-badge">{display}</span>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                    <div style={{
                      padding: '10px 15px', backgroundColor: '#f9fafb', borderTop: '1px solid #e5e7eb',
                      fontSize: '12px', color: '#6b7280', textAlign: 'center'
                    }}>
                      Menampilkan sampel klasifikasi (Maksimal 50 dokumen).
                    </div>
                  </div>
                </>
              )}

              <div style={{ marginTop: '30px', textAlign: 'center', marginBottom: '40px' }}>
                <div style={{ backgroundColor: '#fffbeb', padding: '10px', borderRadius: '8px', border: '1px solid #fde68a', display: 'inline-block', marginBottom: '15px', textAlign: 'left', maxWidth: '600px' }}>
                  <p style={{ margin: 0, fontSize: '13px', color: '#b45309' }}>
                    <strong>💡 Tips Membaca Peta:</strong> Lingkaran yang berdekatan atau menumpuk menandakan bahwa topiknya memiliki pembahasan yang mirip. Semakin besar lingkarannya, semakin banyak ulasan yang membahas topik tersebut.
                  </p>
                </div>
                <br/>
                <button onClick={openFullScreen} className="btn-primary"
                  style={{ padding: '12px 24px', fontSize: '16px', display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                  Buka Visualisasi Peta Topik (Full Tab)
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Analysis;
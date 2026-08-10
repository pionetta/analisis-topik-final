import { useContext, useState, useEffect, useRef } from 'react';
import { AppContext } from '../context/AppContext';
import AnalysisResultView from '../components/AnalysisResultView';

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

  // Total 18 = 2 mode representasi kata (unigram & bigram) x 9 nilai K (2 s.d. 10).
  // Trigram tidak digunakan karena data terlalu jarang muncul pada korpus kecil (100 ulasan/film).
  const [kProgress, setKProgress] = useState({ current: 0, total: 18, currentK: 2 });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const pollRef = useRef(null);

  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

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

  const handleFullAnalysis = async () => {
    if (!prepSteps) {
      showToast("Lakukan preprocessing terlebih dahulu.", 'warning');
      return;
    }
    if (!movieTitle || !movieTitle.trim()) {
      showToast("Isi Nama / Judul Dataset terlebih dahulu.", 'warning');
      return;
    }

    setIsSearchingK(true);
    setOptimalKResults(null);
    setAnalysisResult(null);
    setKProgress({ current: 0, total: 18, currentK: 2 });
    setStatus("Memulai evaluasi Topik 2 sampai 10 (semua K)...");

    try {
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

            const results = task.results || task.result;
            const bestCoh = results.reduce((max, c) => c.score > max.score ? c : max, results[0]);
            
            setOptimalKResults(results);
            setStatus(`Evaluasi selesai. Mode K optimal: ${bestCoh.k} (${bestCoh.mode}). Memuat hasil penuh...`);
            showToast(`Evaluasi selesai! Menampilkan mode ${bestCoh.mode.toUpperCase()} (K=${bestCoh.k})...`, 'success');

            await runAnalyze(bestCoh.k, bestCoh.mode, results);

          } else if (task.status === 'error') {
            clearInterval(pollRef.current);
            setIsSearchingK(false);
            setStatus(`Gagal: ${task.error}`);
            showToast(`Gagal kalkulasi: ${task.error}`, 'error');
          }
        } catch (err) {
          console.error("Error during polling:", err);
          clearInterval(pollRef.current);
          setIsSearchingK(false);
          showToast('Terjadi kesalahan pada saat memproses hasil. Cek console browser.', 'error');
        }
      }, 2000);

    } catch {
      setIsSearchingK(false);
      showToast('Gagal menghubungi server.', 'error');
    }
  };



  const openFullScreen = () => {
    if (!analysisResult?.vis_html) return;
    const newWindow = window.open('', '_blank');
    if (newWindow) {
      newWindow.document.write(analysisResult.vis_html);
      newWindow.document.close();
    }
  };

  const isBusy = isSearchingK || isAnalyzing;
  const progressPct = kProgress.total > 0 ? Math.round((kProgress.current / kProgress.total) * 100) : 0;
  const btnLabel = isSearchingK ? `Mengevaluasi K=${kProgress.currentK} (${kProgress.current}/${kProgress.total})…` : isAnalyzing ? 'Melatih Model LDA Final…' : 'Jalankan Analisis';

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '15px' }}>
        <h1 className="page-title" style={{ margin: 0 }}>Analisis Topik (LDA)</h1>
      </div>

      {!prepSteps ? (
        <div className="card-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <h3 style={{ color: 'var(--text-primary)', margin: '0 0 10px 0', fontSize: '18px' }}>Data Belum Siap</h3>
          <p className="text-muted" style={{ marginBottom: '25px' }}>
            Anda harus menyelesaikan tahapan Preprocessing terlebih dahulu sebelum dapat membangun model LDA.
          </p>
        </div>
      ) : (
        <div>
          <div className="card-container" style={{ marginBottom: '25px' }}>
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
            <button onClick={handleFullAnalysis} className="btn-primary" style={{ width: '100%', padding: '12px', fontSize: '15px' }} disabled={isBusy}>
              {btnLabel}
            </button>
            <p className="text-muted" style={{ marginTop: '12px', textAlign: 'center', fontSize: '13px' }}>
              {status}
            </p>
          </div>

          {(isSearchingK || isAnalyzing) && (
            <div className="card-container" style={{ backgroundColor: 'var(--bg-card)', marginBottom: '25px' }}>
              <h3 className="card-title">Progress Evaluasi</h3>
              {isSearchingK && (
                <div className="progress-wrapper">
                  <p className="progress-label">
                    Mengevaluasi K={kProgress.currentK} <span style={{ color: 'var(--text-secondary)', fontWeight: 'normal' }}>({kProgress.current}/{kProgress.total} selesai)</span>
                  </p>
                  <div className="progress-bar-track">
                    <div className="progress-bar-fill" style={{ width: `${progressPct}%` }} />
                  </div>
                </div>
              )}
              {isAnalyzing && (
                <p style={{ margin: 0, fontSize: '14px', color: 'var(--text-primary)', fontWeight: '600', padding: '10px 0' }}>
                  Melatih model LDA final dengan K={numTopics}...
                </p>
              )}
            </div>
          )}

          {analysisResult && (
            <AnalysisResultView 
              result={analysisResult} 
              optimalKResults={optimalKResults} 
              API_BASE_URL={API_BASE_URL} 
              showToast={showToast} 
              onOpenFullScreen={openFullScreen} 
              onInterpretationSaved={(topicName, label, notes) => {
                // Opsional: perbarui state lokal jika perlu, tapi AnalysisResultView sudah mengelolanya.
                setAnalysisResult(prev => {
                  if (!prev) return prev;
                  return {
                    ...prev,
                    interpretations: {
                      ...(prev.interpretations || {}),
                      [topicName]: { custom_label: label, notes: notes }
                    }
                  }
                });
              }}
            />
          )}
        </div>
      )}
    </div>
  );
}

export default Analysis;

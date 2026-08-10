import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function InfoTip({ text }) {
  const [show, setShow] = useState(false);
  return (
    <span
      style={{ position: 'relative', display: 'inline-flex', marginLeft: '6px', verticalAlign: 'middle' }}
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
      onFocus={() => setShow(true)}
      onBlur={() => setShow(false)}
      tabIndex={0}
    >
      <span
        style={{
          width: '15px', height: '15px', borderRadius: '50%',
          backgroundColor: '#c7c7c7', color: '#fff', fontSize: '10px', fontWeight: 700,
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center', cursor: 'help',
        }}
        aria-label="Info"
      >
        ?
      </span>
      {show && (
        <span
          role="tooltip"
          style={{
            position: 'absolute', bottom: '22px', left: '50%', transform: 'translateX(-50%)',
            backgroundColor: '#272727', color: '#fff', fontSize: '11.5px', lineHeight: 1.45,
            padding: '8px 10px', borderRadius: '6px', width: '200px', zIndex: 20,
            boxShadow: '0 4px 12px rgba(0,0,0,0.18)',
          }}
        >
          {text}
        </span>
      )}
    </span>
  );
}

export default function AnalysisResultView({ 
  result, 
  optimalKResults, 
  API_BASE_URL, 
  showToast,
  onInterpretationSaved,
  onOpenFullScreen
}) {
  const [interpretations, setInterpretations] = useState({});
  const [editingTopic, setEditingTopic] = useState(null);
  const [editBuffer, setEditBuffer] = useState({ label: '', notes: '' });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (result?.topics) {
      const saved = result.interpretations || {};
      const initial = {};
      Object.entries(result.topics).forEach(([topicName, topicData]) => {
        initial[topicName] = saved[topicName] || {
          custom_label: topicData.auto_label || '',
          notes: topicData.auto_notes || ''
        };
      });
      setInterpretations(initial);
    } else {
      setInterpretations({});
    }
  }, [result]);

  const saveInterpretation = async (topicName) => {
    setIsSaving(true);
    try {
      const res = await fetch(`${API_BASE_URL}/update_interpretation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: result.title,
          num_topics: result.num_topics,
          mode: result.ngram_mode || 'bigram',
          topic_id: topicName,
          custom_label: editBuffer.label,
          notes: editBuffer.notes,
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setInterpretations(prev => ({
          ...prev,
          [topicName]: { custom_label: editBuffer.label, notes: editBuffer.notes }
        }));
        setEditingTopic(null);
        showToast(`Label "${topicName}" berhasil disimpan!`, 'success');
        if (onInterpretationSaved) {
          onInterpretationSaved(topicName, editBuffer.label, editBuffer.notes);
        }
      } else {
        showToast(data.error || 'Gagal menyimpan.', 'error');
      }
    } catch {
      showToast('Gagal menghubungi server.', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  if (!result) return null;

  return (
    <div style={{ animation: 'fadeIn 0.4s ease-in-out' }}>
      <h2 className="section-title">Persentase Topik Keseluruhan</h2>
      <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginBottom: '30px' }}>
        {Object.entries(result.overall_distribution || {}).map(([topic, pct], idx) => {
          const label = interpretations[topic]?.custom_label || result.topics?.[topic]?.auto_label || topic;
          return (
            <div key={idx} className="stat-card" style={{ flex: '1 1 200px' }}>
              <div style={{ fontSize: '12px', color: '#717171', fontWeight: '600', marginBottom: '4px' }}>{topic}</div>
              <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#272727' }}>{label}</h4>
              <h2 style={{ margin: 0, color: '#5a5a5a' }}>{pct}%</h2>
            </div>
          );
        })}
      </div>

      <h3 className="section-title" style={{ fontSize: '16px' }}>Interpretasi &amp; Kekuatan Kata Tiap Topik</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        {Object.entries(result.topics || {}).map(([topicName, topicData], i) => {
          const isEditing = editingTopic === topicName;
          const currentInterp = interpretations[topicName] || {};
          const label = currentInterp.custom_label || topicData.auto_label || topicName;
          const displayNote = currentInterp.notes || topicData.auto_notes || '';
          
          return (
            <div key={i} className="card-container" style={{ padding: '20px', marginBottom: 0, display: 'flex', flexDirection: 'column' }}>
              <div style={{ marginBottom: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <span style={{ fontSize: '11px', color: '#717171', fontWeight: '700', textTransform: 'uppercase' }}>{topicName}</span>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editBuffer.label}
                      onChange={e => setEditBuffer({ ...editBuffer, label: e.target.value })}
                      style={{ padding: '6px 10px', fontSize: '16px', fontWeight: 'bold', width: '100%', border: '1px solid #d3d3d3', borderRadius: '4px', marginTop: '4px', boxSizing: 'border-box' }}
                    />
                  ) : (
                    <h3 style={{ margin: '2px 0 0 0', fontSize: '16px', color: '#161616', fontWeight: '700' }}>
                      {label}
                    </h3>
                  )}
                </div>
                {isEditing ? (
                  <div style={{ display: 'flex', gap: '6px', flexDirection: 'column', marginLeft: '10px', flexShrink: 0 }}>
                    <button onClick={() => saveInterpretation(topicName)} disabled={isSaving} className="btn-primary" style={{ padding: '4px 8px', fontSize: '11px' }}>{isSaving ? '...' : 'Simpan'}</button>
                    <button onClick={() => setEditingTopic(null)} style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #d3d3d3', backgroundColor: '#fff', cursor: 'pointer', fontSize: '11px' }}>Batal</button>
                  </div>
                ) : (
                  <button onClick={() => { setEditingTopic(topicName); setEditBuffer({ label: currentInterp.custom_label || topicData.auto_label, notes: currentInterp.notes || '' }); }} style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #e6e6e6', backgroundColor: '#f9f9f9', cursor: 'pointer', fontSize: '11px', marginLeft: '10px', flexShrink: 0 }}>Edit</button>
                )}
              </div>

              {isEditing ? (
                <textarea
                  value={editBuffer.notes}
                  onChange={e => setEditBuffer({ ...editBuffer, notes: e.target.value })}
                  placeholder="Tambahkan catatan analisis..."
                  style={{ width: '100%', height: '80px', padding: '8px', border: '1px solid #d3d3d3', borderRadius: '6px', fontSize: '13px', marginBottom: '16px', boxSizing: 'border-box', resize: 'vertical' }}
                />
              ) : (
                <div style={{ backgroundColor: '#f9f9f9', border: '1px solid #e7e7e7', borderRadius: '8px', padding: '12px 14px', marginBottom: '16px' }}>
                  <div 
                    style={{ margin: 0, fontSize: '13px', color: '#3f3f3f', lineHeight: '1.6' }} 
                    dangerouslySetInnerHTML={{ 
                      __html: displayNote 
                        ? displayNote.replace(/\\n/g, '<br/>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>') 
                        : 'Belum ada catatan analisis.' 
                    }} 
                  />
                </div>
              )}

              <div style={{ marginTop: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr>
                      <th style={{ padding: '8px 0', fontSize: '12px', textAlign: 'left', borderBottom: '1px solid #e6e6e6', color: '#717171' }}>KATA KUNCI</th>
                      <th style={{ padding: '8px 0', fontSize: '12px', textAlign: 'right', borderBottom: '1px solid #e6e6e6', color: '#717171' }}>
                        KONTRIBUSI KATA
                        <InfoTip text="Seberapa besar peran kata ini dalam membentuk makna topik. Semakin panjang batang, semakin dominan kata tersebut." />
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {topicData.words.map((w, idx) => {
                      const maxWeight = topicData.words[0]?.weight || 1;
                      const barPct = Math.min(100, Math.max(10, (w.weight / maxWeight) * 100));
                      return (
                        <tr key={idx}>
                          <td style={{ padding: '6px 0', fontSize: '13.5px', borderBottom: '1px solid #f9f9f9', color: '#272727' }}>{w.word}</td>
                          <td style={{ padding: '6px 0', borderBottom: '1px solid #f9f9f9', textAlign: 'right' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px' }}>
                              <div style={{ width: '65px', height: '6px', backgroundColor: 'var(--border-light)', borderRadius: '3px', overflow: 'hidden' }}>
                                <div style={{ width: `${barPct}%`, height: '100%', backgroundColor: 'var(--accent-blue)', borderRadius: '3px' }} />
                              </div>
                              <span style={{ fontSize: '12px', color: '#535353', fontWeight: '600', minWidth: '42px' }}>
                                {(w.weight * 100).toFixed(1)}%
                              </span>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          );
        })}
      </div>

      <h3 className="section-title" style={{ fontSize: '16px', marginTop: '30px' }}>Seluruh Ulasan Terkait Tiap Topik</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '20px' }}>
        {Object.entries(result.topics || {}).map(([topicName, topicData], idx) => {
          const interp = interpretations[topicName] || {};
          const label = interp?.custom_label || topicData.auto_label || topicName;
          const relatedDocs = (result.document_distributions || []).filter(doc => doc.dominant_topic === topicName);
          
          return (
            <div key={idx} className="card-container" style={{ padding: '20px', marginBottom: 0 }}>
              <h3 style={{ margin: '0 0 15px 0', fontSize: '15px', color: '#000' }}>
                {topicName}: {label} <span style={{ fontSize: '13px', color: '#666', fontWeight: 'normal' }}>({relatedDocs.length} ulasan dominan)</span>
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '400px', overflowY: 'auto', paddingRight: '10px' }}>
                {relatedDocs.length > 0 ? relatedDocs.map((doc, docIdx) => (
                  <div key={docIdx} style={{ backgroundColor: '#f9f9f9', padding: '12px', borderRadius: '8px', border: '1px solid #e0e0e0', fontSize: '13px', lineHeight: '1.5', color: '#333' }}>
                    "{doc.text}"
                  </div>
                )) : (
                  <div style={{ color: '#666', fontSize: '13px', fontStyle: 'italic' }}>Tidak ada ulasan dominan untuk topik ini.</div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: '40px', borderTop: '2px dashed #d3d3d3', paddingTop: '25px', paddingBottom: '30px' }}>
        <details style={{ backgroundColor: '#f9f9f9', borderRadius: '10px', border: '1px solid #e7e7e7', padding: '16px 20px' }}>
          <summary style={{ cursor: 'pointer', fontWeight: '700', fontSize: '15px', color: '#272727' }}>
            📊 Detail Teknis &amp; Evaluasi Model LDA (Klik untuk melihat Perplexity, Coherence, &amp; Grafik K)
          </summary>
          <div style={{ marginTop: '20px' }}>
            <div style={{
              marginBottom: '20px', padding: '16px 20px', borderRadius: '8px',
              display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', backgroundColor: '#272727', color: '#ffffff', flexWrap: 'wrap', gap: '15px'
            }}>
              <div>
                <h4 style={{ margin: '0 0 4px 0', color: '#ffffff' }}>Metrik Evaluasi Model</h4>
                <p style={{ margin: 0, fontSize: '12px', color: '#a0a0a0' }}>
                  Mode: <strong style={{ textTransform: 'uppercase' }}>{result.ngram_mode || 'bigram'}</strong> &bull; K = {result.num_topics}
                </p>
              </div>
              <div style={{ display: 'flex', gap: '25px', textAlign: 'right' }}>
                <div>
                  <p style={{ margin: '0 0 2px 0', fontSize: '11px', color: '#a0a0a0', display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                    Perplexity Score
                    <InfoTip text="Mengukur seberapa cocok model dengan data ulasan. Semakin rendah (semakin negatif), semakin baik." />
                  </p>
                  <h4 style={{ margin: 0, color: '#9c9c9c' }}>{result.perplexity_score || '-'}</h4>
                </div>
                <div>
                  <p style={{ margin: '0 0 2px 0', fontSize: '11px', color: '#a0a0a0', display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                    Coherence Score (Cv)
                    <InfoTip text="Mengukur seberapa mudah topik dipahami manusia. Semakin tinggi nilainya, semakin baik." />
                  </p>
                  <h4 style={{ margin: 0, color: '#9a9a9a' }}>{result.coherence_score}</h4>
                </div>
              </div>
            </div>

            {optimalKResults && (() => {
              const currentMode = result.ngram_mode || 'bigram';
              const filteredKResults = optimalKResults.filter(r => r.mode === currentMode);
              const bestCohFiltered = filteredKResults.reduce((best, r) => (!best || r.score > best.score) ? r : best, null);
              const bestPerpFiltered = filteredKResults.reduce((best, r) => (!best || r.perplexity < best.perplexity) ? r : best, null);

              return (
                <div style={{ backgroundColor: '#ffffff', padding: '16px', borderRadius: '8px', border: '1px solid #e7e7e7' }}>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: '700', color: '#161616' }}>
                    Tabel Hasil Kalkulasi Mode <span style={{ color: '#5a5a5a', textTransform: 'uppercase' }}>{currentMode}</span>
                  </h4>
                  <div style={{
                    maxHeight: '180px', overflowY: 'auto', border: '1px solid #e6e6e6',
                    borderRadius: '6px', marginBottom: '20px'
                  }}>
                    <table style={{ width: '100%', fontSize: '12px', backgroundColor: '#ffffff', borderCollapse: 'collapse', marginTop: 0 }}>
                      <thead style={{ position: 'sticky', top: 0, backgroundColor: '#f3f3f3', zIndex: 1 }}>
                        <tr>
                          <th style={{ padding: '8px', textAlign: 'center', borderBottom: '1px solid #e6e6e6' }}>Jumlah Topik (K)</th>
                          <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #e6e6e6' }}>Coherence</th>
                          <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #e6e6e6' }}>Perplexity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredKResults.map((res, i) => {
                          const isCoh = bestCohFiltered?.k === res.k;
                          const isPerp = bestPerpFiltered?.k === res.k;
                          const isActive = Number(result.num_topics) === res.k;
                          return (
                            <tr key={i} style={{
                              backgroundColor: isActive ? 'var(--bg-subtle)' : (isCoh ? 'var(--bg-app)' : 'transparent'),
                              borderLeft: isCoh ? '3px solid var(--accent-mint)' : '3px solid transparent',
                            }}>
                              <td style={{ padding: '8px', borderBottom: '1px solid #f3f3f3', textAlign: 'center', fontWeight: 'bold' }}>
                                K = {res.k}
                                {isActive && <span style={{ color: '#5a5a5a', fontSize: '11px', marginLeft: '5px', fontWeight: '600' }}>[Aktif]</span>}
                              </td>
                              <td style={{ padding: '8px', borderBottom: '1px solid #f3f3f3', textAlign: 'right', color: isCoh ? '#676767' : '#535353', fontWeight: isCoh ? '700' : 'normal' }}>
                                {res.score.toFixed(4)}
                              </td>
                              <td style={{ padding: '8px', borderBottom: '1px solid #f3f3f3', textAlign: 'right', color: isPerp ? '#656565' : '#535353', fontWeight: isPerp ? '700' : 'normal' }}>
                                {res.perplexity.toFixed(4)}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#535353' }}>Grafik Pengujian K</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    {[
                      { label: '📈 Coherence Score (Semakin Tinggi = Lebih Jelas/Fokus)', key: 'score', color: 'var(--accent-mint-text)', tColor: 'var(--text-secondary)' },
                      { label: '📉 Perplexity Score (Semakin Rendah = Lebih Bagus)', key: 'perplexity', color: 'var(--accent-blue-text)', tColor: 'var(--text-secondary)' },
                    ].map(({ label, key, color, tColor }) => (
                      <div key={key} style={{ backgroundColor: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e6e6e6' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                          <span style={{ fontSize: '12px', fontWeight: '600', color: tColor }}>{label}</span>
                        </div>
                        <ResponsiveContainer width="100%" height={120}>
                          <LineChart data={filteredKResults} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e6e6e6" />
                            <XAxis dataKey="k" tick={{ fontSize: 11 }} />
                            <YAxis tick={{ fontSize: 11, fill: color }} axisLine={false} tickLine={false} domain={['auto', 'auto']} />
                            <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
                            <Line type="monotone" dataKey={key} stroke={color} strokeWidth={2} activeDot={{ r: 6 }} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}

            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <button onClick={onOpenFullScreen} className="btn-primary" style={{ padding: '10px 24px', fontSize: '14px' }}>
                Buka Visualisasi Peta Topik (pyLDAvis) di Layar Penuh
              </button>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}

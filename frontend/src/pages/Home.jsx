/* eslint-disable no-unused-vars */
import { useContext, useState } from 'react';
import { AppContext } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';

function Home() {
  const {
    setFile, handleUpload, status, columns, setColumns, previewData, setPreviewData,
    selectedColumn, setSelectedColumn, handlePreprocess, showToast
  } = useContext(AppContext);

  const [fileName, setFileName] = useState("");
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFile(file);
      setFileName(file.name);
      setPreviewData([]);
    }
  };

  const runPreprocessAndNavigate = async () => {
    const success = await handlePreprocess();
    if (success) {
      navigate('/preprocessing');
    } else {
      showToast('Proses preprocessing gagal. Pastikan file sudah diunggah.', 'error');
    }
  };

  const truncateText = (text, maxLength = 80) => {
    if (!text) return "";
    const str = String(text);
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
  };

  return (
    <div>
      <h1 style={{ fontSize: '24px', marginBottom: '25px', color: '#242424' }}>Upload Dataset</h1>

      <div className="card-container">
        <h3 style={{ marginTop: 0, fontSize: '16px', marginBottom: '20px' }}>Pilih File CSV</h3>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            <label className="btn-browse">
              Pilih File

              <input type="file" accept=".csv" onChange={handleFileChange} style={{ display: 'none' }} />
            </label>
            <span style={{ fontSize: '13px', color: '#717171' }}>
              {fileName || "Tidak ada file dipilih"}
            </span>
          </div>


          <button
            onClick={handleUpload}
            className="btn-primary"
            disabled={status === "Sedang mengunggah file..."}
          >
            {status === "Sedang mengunggah file..." ? "Mengunggah..." : "Unggah"}
          </button>
        </div>
        <p style={{ fontSize: '13px', color: '#717171', marginTop: '20px' }}>Status: {status}</p>
      </div>

      {columns.length > 0 && (
        <>
          <div className="card-container scroll-x">
            <p style={{ fontSize: '13px', color: '#717171', margin: '0 0 15px 0' }}>
              Menampilkan 5 baris pertama dataset.
            </p>
            <table style={{ width: '100%' }}>
              <thead>
                <tr>{columns.map((c, i) => <th key={i}>{c}</th>)}</tr>
              </thead>
              <tbody>
                {previewData.map((r, i) => (
                  <tr key={i}>
                    {columns.map((c, j) => (
                      <td
                        key={j}
                        title={r[c]} // Menampilkan teks penuh saat di-hover
                        style={{ fontSize: '13px', lineHeight: '1.6', color: '#717171' }}
                      >
                        {truncateText(r[c])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* KARTU: PEMILIHAN KOLOM & TRIGGER PREPROCESSING */}
          <div className="card-container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ marginTop: 0, fontSize: '16px', marginBottom: '10px' }}>Konfigurasi Analisis</h3>
              <p style={{ fontSize: '13px', color: '#717171', margin: 0 }}>
                Pilih kolom yang berisi teks ulasan.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
              <select
                value={selectedColumn}
                onChange={(e) => setSelectedColumn(e.target.value)}
                style={{
                  padding: '10px',
                  borderRadius: '6px',
                  border: '1px solid #e6e6e6',
                  backgroundColor: '#f9f9f9',
                  fontSize: '14px',
                  minWidth: '200px',
                  outline: 'none'
                }}
              >
                {columns.map((c, i) => (
                  <option key={i} value={c}>{c}</option>
                ))}
              </select>


              <button
                onClick={runPreprocessAndNavigate}
                className="btn-primary"
                disabled={status.includes("Sedang memproses")}
              >
                {status.includes("Sedang memproses") ? "Memproses..." : "Jalankan Preprocessing"}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Home;

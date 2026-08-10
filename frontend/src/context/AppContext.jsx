/* eslint-disable react-refresh/only-export-components, react-hooks/set-state-in-effect */
import { createContext, useState, useEffect, useCallback } from 'react';

export const AppContext = createContext();

export function AppProvider({ children }) {
  // Saat production (HuggingFace), VITE_API_URL dikosongkan di .env.production
  // agar fetch menggunakan relative URL (same-origin dengan Flask).
  // Saat dev, fallback ke localhost Flask.
  let API_BASE_URL = import.meta.env.VITE_API_URL !== undefined
    ? import.meta.env.VITE_API_URL          // '' (production) atau 'http://...' (dev .env)
    : 'http://127.0.0.1:5000';              // fallback jika VITE_API_URL tidak di-set sama sekali
    
  if (API_BASE_URL.endsWith('/')) {
    API_BASE_URL = API_BASE_URL.slice(0, -1);
  }

  // ==========================================
  // STATE APLIKASI
  // ==========================================
  const [file,              setFile]              = useState(null);
  const [uploadedFilename,  setUploadedFilename]  = useState('');
  const [columns,           setColumns]           = useState([]);
  const [previewData,       setPreviewData]       = useState([]);
  const [selectedColumn,    setSelectedColumn]    = useState('');
  const [status,            setStatus]            = useState('');
  const [prepSteps,         setPrepSteps]         = useState(null);
  const [movieTitle,        setMovieTitle]        = useState('');
  const [numTopics,         setNumTopics]         = useState(3);
  const [analysisResult,    setAnalysisResult]    = useState(null);
  const [savedMovies,       setSavedMovies]       = useState([]);
  const [selectedSavedMovie, setSelectedSavedMovie] = useState('');
  const [optimalKResults,   setOptimalKResults]   = useState(null);
  const [isSearchingK,      setIsSearchingK]      = useState(false);



  // ==========================================
  // TOAST NOTIFICATION STATE
  // ==========================================
  const [toast, setToast] = useState(null); // { message: string, type: 'success'|'error'|'info'|'warning' }

  const showToast = useCallback((message, type = 'info') => {
    setToast({ message, type });
  }, []);

  const dismissToast = useCallback(() => {
    setToast(null);
  }, []);

  // ==========================================
  // FUNGSI FETCH HISTORY
  // ==========================================
  const fetchSavedMovies = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/saved_movies`);
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') setSavedMovies(data.data);
      }
    } catch { 
      console.error("Gagal memuat daftar history");
    }
  }, [API_BASE_URL]);

  useEffect(() => {
    fetchSavedMovies();
  }, [fetchSavedMovies]);

  // ==========================================
  // FUNGSI UPLOAD
  // ==========================================
  const handleUpload = async () => {
    if (!file) {
      showToast("Pilih file terlebih dahulu.", "warning");
      return;
    }
    setStatus("Sedang mengunggah file...");
    setColumns([]);
    setPreviewData([]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        setStatus(`Gagal: Kesalahan internal server (${response.status})`);
        showToast(`Gagal mengunggah: Error ${response.status}`, "error");
        return;
      }

      const data = await response.json();
      if (data.status === 'success') {
        setColumns(data.columns);
        setPreviewData(data.preview);
        setUploadedFilename(data.filename);
        if (data.columns.length > 0) setSelectedColumn(data.columns[0]);
        setStatus(`Sukses: Berhasil mengunggah dataset.`);
        showToast("File berhasil diunggah!", "success");

        // [PERBAIKAN] Reset seluruh hasil analisis sebelumnya agar halaman
        // Analysis bersih saat dataset baru diunggah
        setAnalysisResult(null);
        setOptimalKResults(null);
        setPrepSteps(null);

        // [PERBAIKAN] Auto-fill judul dari nama file:
        // hapus ekstensi (.csv), ganti _ dan - dengan spasi, lalu Title Case
        const autoTitle = data.filename
          .replace(/\.[^/.]+$/, '')           // hapus ekstensi
          .replace(/[_-]+/g, ' ')             // underscore/dash â†’ spasi
          .replace(/\b\w/g, c => c.toUpperCase()); // Title Case
        setMovieTitle(autoTitle);

      } else {
        setStatus(`Gagal: ${data.error}`);
        showToast(data.error, "error");
      }
    } catch { 
      setStatus("Gagal menghubungi server backend Flask.");
      showToast("Tidak dapat terhubung ke server.", "error");
    }
  };

  // ==========================================
  // FUNGSI PREPROCESSING
  // ==========================================
  const handlePreprocess = async () => {
    if (!selectedColumn || !uploadedFilename) {
      showToast("Pastikan file diunggah dan kolom dipilih.", "warning");
      return false;
    }
    setStatus("Sedang memproses dan membersihkan teks... Mohon tunggu.");

    try {
      const response = await fetch(`${API_BASE_URL}/preprocess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ column: selectedColumn, filename: uploadedFilename })
      });

      if (!response.ok) {
        setStatus(`Gagal: Kesalahan internal server (${response.status})`);
        showToast(`Gagal preprocessing: Error ${response.status}`, "error");
        return false;
      }

      const data = await response.json();
      if (data.status === 'success') {
        setPrepSteps({ ...data.data, stats: data.stats });
        setStatus("Sukses: Preprocessing selesai!");
        showToast("Preprocessing selesai!", "success");
        return true;
      } else {
        setStatus(`Gagal Preprocessing: ${data.error}`);
        showToast(data.error, "error");
        return false;
      }
    } catch { 
      setStatus("Gagal menghubungi server backend Flask.");
      showToast("Tidak dapat terhubung ke server.", "error");
      return false;
    }
  };

  return (
    <AppContext.Provider value={{
      API_BASE_URL,
      // File & Upload
      file, setFile,
      uploadedFilename, setUploadedFilename,
      columns, setColumns,
      previewData, setPreviewData,
      selectedColumn, setSelectedColumn,
      // Status & Steps
      status, setStatus,
      prepSteps, setPrepSteps,
      // Analisis
      movieTitle, setMovieTitle,
      numTopics, setNumTopics,
      analysisResult, setAnalysisResult,
      // History
      savedMovies, setSavedMovies,
      selectedSavedMovie, setSelectedSavedMovie,
      // Optimal K & N-Gram
      optimalKResults, setOptimalKResults,
      isSearchingK, setIsSearchingK,

      // Toast
      toast, showToast, dismissToast,
      // Actions
      fetchSavedMovies,
      handleUpload,
      handlePreprocess,
    }}>
      {children}
    </AppContext.Provider>
  );
}


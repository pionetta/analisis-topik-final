import { useContext, useEffect } from 'react';
import { AppContext } from '../context/AppContext';

/**
 * Komponen Toast Notification global.
 * Menggantikan window.alert() di seluruh aplikasi.
 * Otomatis hilang setelah 4 detik.
 */
function Toast() {
  const { toast, dismissToast } = useContext(AppContext);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(dismissToast, 4000);
    return () => clearTimeout(timer);
  }, [toast, dismissToast]);

  if (!toast) return null;

  const styles = {
    success: { textColor: '#414141', icon: '✓', className: 'toast toast-success' },
    error:   { textColor: '#404040', icon: '✕', className: 'toast toast-error'   },
    info:    { textColor: '#424242', icon: 'ℹ', className: 'toast toast-info'    },
    warning: { textColor: '#525252', icon: '⚠', className: 'toast toast-warning' },
  };

  const s = styles[toast.type] || styles.info;

  return (
    <div className={s.className} role="alert" aria-live="assertive">
      <span className="toast-icon" style={{ color: s.textColor }}>{s.icon}</span>
      <p className="toast-message" style={{ color: s.textColor }}>{toast.message}</p>
      <button className="toast-close" onClick={dismissToast} aria-label="Tutup notifikasi"
        style={{ color: s.textColor }}>
        ×
      </button>
    </div>
  );
}

export default Toast;

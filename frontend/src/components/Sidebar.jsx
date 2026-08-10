import { Link, useLocation } from 'react-router-dom';

function Sidebar() {
  const location = useLocation();
  const linkStyle = (path) => ({
    textDecoration: 'none',
    color: location.pathname === path ? '#ffffff' : 'var(--text-secondary)',
    backgroundColor: location.pathname === path ? '#111111' : 'transparent',
    padding: '12px 16px',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: location.pathname === path ? '700' : '500',
    display: 'block',
    marginBottom: '8px',
    transition: 'all 0.2s ease',
    boxShadow: location.pathname === path ? '0 2px 4px rgba(0,0,0,0.1)' : 'none'
  });

  return (
    <nav style={{ width: '260px', backgroundColor: 'var(--bg-card)', borderRight: '1px solid var(--border-light)', padding: '30px 20px', position: 'fixed', height: '100vh', boxSizing: 'border-box', overflowY: 'auto' }}>
      
      {/* Judul dibuat menjadi link agar bisa kembali ke halaman Welcome (Beranda) */}
      <Link to="/" style={{ textDecoration: 'none', display: 'block', marginBottom: '40px', padding: '0 16px' }}>
        <h2 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.5px' }}>Analisis Topik</h2>
      </Link>

      <Link to="/home"          style={linkStyle('/home')}>Upload Dataset</Link>
      <Link to="/preprocessing" style={linkStyle('/preprocessing')}>Preprocessing Data</Link>
      <Link to="/analysis"      style={linkStyle('/analysis')}>Topic Analysis</Link>
      <Link to="/history"       style={linkStyle('/history')}>History</Link>
      {/* Link Visualization dinonaktifkan secara sengaja */}
      {/* <Link to="/visualization" style={linkStyle('/visualization')}>Peta Topik Interaktif</Link> */}
    </nav>
  );
}

export default Sidebar;
import { Component } from 'react';

/**
 * React Error Boundary — menangkap crash komponen manapun
 * dan menampilkan UI fallback yang ramah pengguna,
 * daripada membiarkan layar putih/blank.
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
    this.handleReset = this.handleReset.bind(this);
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary] Terjadi crash pada komponen:', error, info);
  }

  handleReset() {
    this.setState({ hasError: false, error: null });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', minHeight: '60vh', textAlign: 'center', padding: '40px 20px'
        }}>
          <div style={{ fontSize: '52px', marginBottom: '20px' }}>💥</div>
          <h2 style={{ color: '#5c5c5c', marginBottom: '10px', fontSize: '20px' }}>
            Terjadi Kesalahan Tak Terduga
          </h2>
          <p style={{ color: '#717171', marginBottom: '20px', maxWidth: '520px', lineHeight: '1.6' }}>
            Komponen ini mengalami error dan tidak dapat ditampilkan.
            Silakan muat ulang halaman atau kembali ke halaman sebelumnya.
          </p>
          {this.state.error?.message && (
            <p style={{
              fontFamily: 'monospace', fontSize: '12px', color: '#a2a2a2',
              background: '#f3f3f3', padding: '10px 18px',
              borderRadius: '8px', marginBottom: '24px', maxWidth: '520px',
              wordBreak: 'break-all', textAlign: 'left'
            }}>
              {this.state.error.message}
            </p>
          )}
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={this.handleReset}
              style={{ background: '#f3f3f3', border: '1px solid #e6e6e6', color: '#3f3f3f',
                padding: '10px 24px', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' }}
            >
              Coba Lagi
            </button>
            <button
              onClick={() => window.location.reload()}
              style={{ backgroundColor: '#242424', color: '#ffffff', border: 'none',
                padding: '10px 24px', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' }}
            >
              Muat Ulang Halaman
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

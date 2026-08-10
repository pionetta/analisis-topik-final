import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Sidebar from './components/Sidebar';
import Toast from './components/Toast';
import ErrorBoundary from './components/ErrorBoundary';
import Welcome from './pages/Welcome';
import Home from './pages/Home';
import Preprocessing from './pages/Preprocessing';
import Analysis from './pages/Analysis';
import History from './pages/History';

import './index.css';
import './app.css';

function AppLayout() {
  const SIDEBAR_W = 260;
  const location = useLocation();
  const isLanding = location.pathname === '/';

  return (
    <div style={{ display: 'flex', width: '100%', minHeight: '100vh', backgroundColor: '#f9f9f9' }}>
      {!isLanding && <Sidebar />}

      <div style={{
        flex: 1,
        padding:    isLanding ? '0' : '30px',
        marginLeft: isLanding ? '0' : `${SIDEBAR_W}px`,
        transition: 'margin-left 0.2s ease',
      }}>
        <ErrorBoundary>
          <Routes>
            <Route path="/"              element={<Welcome />}       />
            <Route path="/home"          element={<Home />}          />
            <Route path="/preprocessing" element={<Preprocessing />} />
            <Route path="/analysis"      element={<Analysis />}      />
            <Route path="/history"       element={<History />}       />
          </Routes>
        </ErrorBoundary>
      </div>

      <Toast />
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <Router>
        <AppLayout />
      </Router>
    </AppProvider>
  );
}

export default App;
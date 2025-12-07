/**
 * Main App Component
 */
import { useState, useEffect } from 'react';
import LandingPage from './pages/LandingPage';
import FloatingChatbot from './components/FloatingChatbot';
import { healthAPI } from './services/api';

function App() {
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await healthAPI.check();
      setBackendStatus('connected');
    } catch (error) {
      console.error('Backend not available:', error);
      setBackendStatus('disconnected');
    }
  };

  return (
    <div className="App">
      {/* Backend Status Indicator */}
      {backendStatus === 'disconnected' && (
        <div className="fixed top-0 left-0 right-0 bg-red-500 text-white text-center py-2 z-50">
          ⚠️ Backend tidak terhubung. Pastikan Flask server berjalan di http://localhost:8000
        </div>
      )}

      {/* Main Landing Page */}
      <LandingPage />

      {/* Floating Chatbot Widget */}
      <div className="floating-chatbot-trigger">
        <FloatingChatbot />
      </div>
    </div>
  );
}

export default App;

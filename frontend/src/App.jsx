/**
 * Main App Component
 * Wrapped dengan PersonalizationProvider untuk state management global
 */
import { useState, useEffect } from 'react';
import LandingPage from './pages/LandingPage';
import FloatingChatbot from './components/FloatingChatbot';
import { PersonalizationProvider } from './contexts/PersonalizationContext';
import { healthAPI } from './services/api';

/**
 * Loading Skeleton Component
 * Menampilkan skeleton screen saat app loading
 */
const LoadingSkeleton = () => (
  <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
    {/* Header Skeleton */}
    <div className="bg-white border-b border-gray-200 animate-pulse">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto text-center">
          <div className="h-10 bg-gray-200 rounded w-2/3 mx-auto mb-4"></div>
          <div className="h-6 bg-gray-100 rounded w-1/2 mx-auto mb-6"></div>
          <div className="flex justify-center gap-8">
            <div className="h-4 bg-gray-100 rounded w-24"></div>
            <div className="h-4 bg-gray-100 rounded w-24"></div>
            <div className="h-4 bg-gray-100 rounded w-24"></div>
          </div>
        </div>
      </div>
    </div>
    
    {/* Content Skeleton */}
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm p-4 animate-pulse">
              <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-100 rounded w-1/2 mb-2"></div>
              <div className="h-4 bg-gray-100 rounded w-full"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

/**
 * App Content Component
 * Konten utama aplikasi setelah mounted
 */
const AppContent = () => {
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await healthAPI.check();
      setBackendStatus('connected');
      console.log('✓ Backend connected');
    } catch (error) {
      console.error('Backend not available:', error);
      setBackendStatus('disconnected');
    }
  };

  return (
    <div className="App" style={{ minHeight: '100vh', width: '100%' }}>
      {/* Backend Status Indicator */}
      {backendStatus === 'disconnected' && (
        <div className="fixed top-0 left-0 right-0 bg-red-500 text-white text-center py-2 z-50">
          ⚠️ Backend tidak terhubung. Pastikan Flask server berjalan di http://localhost:5500
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
};

/**
 * Main App Component
 * Entry point dengan PersonalizationProvider untuk state management
 */
function App() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <LoadingSkeleton />;
  }

  return (
    <PersonalizationProvider>
      <AppContent />
    </PersonalizationProvider>
  );
}

export default App;

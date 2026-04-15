/**
 * Main App Component — LombokEats
 * Wrapped dengan PersonalizationProvider untuk state management global.
 * Coordinates chatbot open state between Navbar/Hero CTAs and FloatingChatbot.
 */
import { useState, useEffect } from 'react';
import LandingPage from './pages/LandingPage';
import FloatingChatbot from './components/FloatingChatbot';
import RestaurantDetailModal from './components/RestaurantDetailModal';
import { PersonalizationProvider } from './contexts/PersonalizationContext';
import { healthAPI } from './services/api';

/**
 * Loading Skeleton Component
 * Premium skeleton screen matching LombokEats design
 */
const LoadingSkeleton = () => (
  <div className="min-h-screen bg-white">
    {/* Navbar Skeleton */}
    <div className="h-16 bg-white/80 backdrop-blur-xl border-b border-gray-100 animate-pulse">
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
        <div className="h-7 bg-gray-100 rounded-lg w-36" />
        <div className="hidden md:flex gap-6">
          <div className="h-4 bg-gray-100 rounded w-16" />
          <div className="h-4 bg-gray-100 rounded w-16" />
          <div className="h-4 bg-gray-100 rounded w-16" />
          <div className="h-9 bg-primary-100 rounded-2xl w-24" />
        </div>
      </div>
    </div>

    {/* Hero Skeleton */}
    <div className="max-w-7xl mx-auto px-6 py-24">
      <div className="grid lg:grid-cols-2 gap-16 items-center">
        <div className="space-y-6 animate-pulse">
          <div className="h-6 bg-primary-50 rounded-full w-48" />
          <div className="space-y-3">
            <div className="h-10 bg-gray-100 rounded-xl w-full" />
            <div className="h-10 bg-gray-100 rounded-xl w-4/5" />
            <div className="h-10 bg-gray-100 rounded-xl w-3/5" />
          </div>
          <div className="h-5 bg-gray-50 rounded-lg w-3/4" />
          <div className="flex gap-4">
            <div className="h-14 bg-primary-100 rounded-2xl w-40" />
            <div className="h-14 bg-gray-100 rounded-2xl w-36" />
          </div>
        </div>
        <div className="hidden lg:block animate-pulse">
          <div className="w-[380px] h-[480px] bg-gray-50 rounded-3xl border border-gray-100" />
        </div>
      </div>
    </div>

    {/* Cards Skeleton */}
    <div className="max-w-7xl mx-auto px-6 py-12">
      <div className="text-center mb-10 animate-pulse">
        <div className="h-7 bg-gray-100 rounded-xl w-64 mx-auto mb-3" />
        <div className="h-4 bg-gray-50 rounded w-96 mx-auto" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-pulse">
            <div className="h-52 bg-gray-100" />
            <div className="p-5 space-y-3">
              <div className="h-5 bg-gray-100 rounded-lg w-3/4" />
              <div className="h-4 bg-gray-50 rounded w-1/2" />
              <div className="h-10 bg-gray-50 rounded-xl" />
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

/**
 * App Content Component
 */
const AppContent = () => {
  const [backendStatus, setBackendStatus] = useState('checking');
  const [chatOpen, setChatOpen] = useState(false);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);

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
    <div className="App font-poppins" style={{ minHeight: '100vh', width: '100%' }}>
      {/* Backend Status Indicator */}
      {backendStatus === 'disconnected' && (
        <div className="fixed top-0 left-0 right-0 bg-red-500 text-white text-center py-2 z-[60] text-sm font-medium">
          ⚠️ Backend tidak terhubung — Pastikan Flask server berjalan di http://localhost:5500
        </div>
      )}

      {/* Main Landing Page */}
      <LandingPage 
        onOpenChat={() => setChatOpen(true)} 
        onViewDetail={setSelectedRestaurant} 
      />

      {/* Floating Chatbot Widget */}
      <FloatingChatbot
        forceOpen={chatOpen}
        onClose={() => setChatOpen(false)}
        onViewDetail={setSelectedRestaurant}
      />

      {/* Detail Modal Overlay */}
      <RestaurantDetailModal 
        restaurant={selectedRestaurant} 
        onClose={() => setSelectedRestaurant(null)} 
      />
    </div>
  );
};

/**
 * Main App
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

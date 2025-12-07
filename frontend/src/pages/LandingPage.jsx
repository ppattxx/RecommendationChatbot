/**
 * Landing Page Component
 * Halaman utama dengan rekomendasi restoran berdasarkan preferensi user
 */
import { useState, useEffect } from 'react';
import { FiMapPin, FiStar, FiUsers, FiRefreshCw } from 'react-icons/fi';
import { preferencesAPI, chatAPI } from '../services/api';
import RestaurantRecommendations from '../components/RestaurantRecommendations';

const LandingPage = () => {
  const [preferences, setPreferences] = useState(null);
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPreferences();
    fetchSummary();
  }, []);

  const handleResetHistory = async () => {
    if (confirm('Yakin ingin mereset SEMUA riwayat chat dan preferensi dari database? Ini akan menghapus semua data dan tidak bisa dikembalikan!')) {
      try {
        // Call API to delete ALL data from database
        const response = await chatAPI.resetAllChatHistory();
        console.log('Reset ALL response:', response);
        
        // Clear localStorage
        localStorage.removeItem('session_id');
        localStorage.removeItem('device_token');
        localStorage.removeItem('session_timestamp');
        localStorage.removeItem('chat_history');
        
        // Show success message
        alert(`Berhasil menghapus ${response.data.deleted_chats} riwayat chat!`);
        
        // Reload page to refresh
        window.location.reload();
      } catch (error) {
        console.error('Error resetting history:', error);
        alert('Gagal mereset history. Silakan coba lagi.');
      }
    }
  };

  const fetchPreferences = async () => {
    try {
      setIsLoading(true);
      const sessionId = localStorage.getItem('session_id');
      const deviceToken = localStorage.getItem('device_token');

      const response = await preferencesAPI.getUserPreferences({
        session_id: sessionId || undefined,
        device_token: deviceToken || undefined
      });
      if (response.success) {
        setPreferences(response.data);
      }
    } catch (err) {
      console.error('Error fetching preferences:', err);
      setError('Gagal memuat data preferensi');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await preferencesAPI.getPreferencesSummary();
      if (response.success) {
        setSummary(response.data);
      }
    } catch (err) {
      console.error('Error fetching summary:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Memuat data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-gray-800 mb-2">
                Temukan Tempat Terbaik di Lombok
              </h1>
              <p className="text-lg text-gray-600 mb-6">
                Rekomendasi personal berdasarkan preferensi dan riwayat Anda
              </p>
              
              {/* Quick Stats */}
              <div className="flex justify-center items-center gap-8 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <FiMapPin className="w-4 h-4" />
                  <span>500+ Tempat</span>
                </div>
                <div className="flex items-center gap-2">
                  <FiStar className="w-4 h-4" />
                  <span>Rating Terpercaya</span>
                </div>
                <div className="flex items-center gap-2">
                  <FiUsers className="w-4 h-4" />
                  <span>1000+ Ulasan</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="text-center flex justify-center gap-4">
              <button 
                onClick={() => document.querySelector('.floating-chatbot-trigger')?.click()}
                className="bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-8 rounded-full transition-colors shadow-lg"
              >
                💬 Chat untuk Rekomendasi Personal
              </button>
              <button
                onClick={handleResetHistory}
                className="flex items-center gap-2 px-6 py-3 text-sm font-semibold text-red-600 hover:text-white hover:bg-red-600 border-2 border-red-600 rounded-full transition-colors"
                title="Reset semua riwayat dan preferensi"
              >
                <FiRefreshCw size={18} />
                Reset History
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Restaurant Recommendations */}
          <RestaurantRecommendations userPreferences={preferences} />
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            © 2025 Chatbot Rekomendasi Restoran - Tugas Akhir
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Powered by Content-Based Filtering & Flask + React
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

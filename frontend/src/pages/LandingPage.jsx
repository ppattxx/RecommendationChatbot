/**
 * Landing Page Component
 * Halaman utama dengan rekomendasi restoran berdasarkan preferensi user
 * Terintegrasi dengan PersonalizationContext untuk seamless updates
 */
import { useEffect } from 'react';
import { FiMapPin, FiStar, FiUsers, FiRefreshCw } from 'react-icons/fi';
import { usePersonalization } from '../contexts/PersonalizationContext';
import RestaurantRecommendations from '../components/RestaurantRecommendations';

const LandingPage = () => {
  // Get context values for seamless updates
  const { 
    preferences: contextPreferences,
    isLoadingPreferences,
    fetchPreferences,
    resetAllData
  } = usePersonalization();

  // Fetch preferences on mount
  useEffect(() => {
    fetchPreferences();
  }, []);

  const handleResetHistory = async () => {
    if (confirm('Yakin ingin mereset SEMUA riwayat chat dan preferensi dari database? Ini akan menghapus semua data dan tidak bisa dikembalikan!')) {
      try {
        const success = await resetAllData();
        
        if (success) {
          alert('Berhasil menghapus semua riwayat!');
          window.location.reload();
        } else {
          alert('Gagal mereset history. Silakan coba lagi.');
        }
      } catch (error) {
        console.error('Error resetting history:', error);
        alert('Gagal mereset history. Silakan coba lagi.');
      }
    }
  };

  // Show loading skeleton
  if (isLoadingPreferences && !contextPreferences) {
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

      {/* Main Content - Top 5 Recommendations Only */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <RestaurantRecommendations userPreferences={contextPreferences} />
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            © 2025 Chatbot Rekomendasi Restoran - Tugas Akhir
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Powered by Content-Based Filtering dengan Cosine Similarity
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

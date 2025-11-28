/**
 * Landing Page Component
 * Halaman utama dengan analisis preferensi user
 */
import { useState, useEffect } from 'react';
import { FiTrendingUp, FiMapPin, FiHeart, FiMessageSquare } from 'react-icons/fi';
import { preferencesAPI } from '../services/api';
import {
  CuisineChart,
  LocationPieChart,
  ActivityChart,
  PreferenceStatsCard,
  MoodsList,
  TopSearchesList,
} from '../components/PreferenceCharts';

const LandingPage = () => {
  const [preferences, setPreferences] = useState(null);
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPreferences();
    fetchSummary();
  }, []);

  const fetchPreferences = async () => {
    try {
      setIsLoading(true);
      const response = await preferencesAPI.getUserPreferences();
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
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-4">
               Chatbot Rekomendasi Restoran
            </h1>
            <p className="text-xl text-primary-100 mb-8">
              Temukan restoran terbaik berdasarkan preferensi Anda dengan teknologi Content-Based Filtering
            </p>
            <div className="flex justify-center gap-4">
              <button 
                onClick={() => document.querySelector('.floating-chatbot-trigger')?.click()}
                className="bg-white text-primary-700 font-semibold py-3 px-8 rounded-full hover:bg-primary-50 transition-colors shadow-lg"
              >
                Mulai Chat Sekarang
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="container mx-auto px-4 -mt-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <PreferenceStatsCard
            title="Total Percakapan"
            value={summary?.total_conversations || 0}
            icon={<FiMessageSquare size={24} />}
            color="primary"
          />
          <PreferenceStatsCard
            title="Masakan Favorit"
            value={summary?.top_cuisine || '-'}
            icon={<FiTrendingUp size={24} />}
            color="success"
          />
          <PreferenceStatsCard
            title="Lokasi Favorit"
            value={summary?.top_location || '-'}
            icon={<FiMapPin size={24} />}
            color="warning"
          />
          <PreferenceStatsCard
            title="Sesi Aktif"
            value={summary?.total_sessions || 0}
            icon={<FiHeart size={24} />}
            color="danger"
          />
        </div>

        {/* Main Content */}
        {preferences && preferences.total_conversations > 0 ? (
          <div className="space-y-8 pb-12">
            {/* Analisis Minat Section */}
            <div className="card">
              <h2 className="text-3xl font-bold text-gray-800 mb-2">
                📊 Analisis Minat Anda
              </h2>
              <p className="text-gray-600 mb-6">
                Berdasarkan {preferences.total_conversations} percakapan yang telah Anda lakukan
              </p>
              
              {preferences.summary && (
                <div className="bg-primary-50 border-l-4 border-primary-500 p-4 rounded mb-6">
                  <h3 className="font-semibold text-primary-900 mb-2">Preferensi Utama Anda:</h3>
                  <ul className="space-y-1 text-primary-800">
                    {preferences.summary.most_searched_cuisine && (
                      <li>🍕 Paling suka: <strong>{preferences.summary.most_searched_cuisine}</strong></li>
                    )}
                    {preferences.summary.most_visited_location && (
                      <li>📍 Sering ke: <strong>{preferences.summary.most_visited_location}</strong></li>
                    )}
                    {preferences.summary.favorite_mood && (
                      <li>✨ Suasana favorit: <strong>{preferences.summary.favorite_mood}</strong></li>
                    )}
                  </ul>
                </div>
              )}
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Cuisine Preferences */}
              <div className="card">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  🍜 Jenis Masakan Favorit
                </h3>
                <CuisineChart data={preferences.preferred_cuisines} />
              </div>

              {/* Location Preferences */}
              <div className="card">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  📍 Lokasi yang Sering Dicari
                </h3>
                <LocationPieChart data={preferences.preferred_locations} />
              </div>

              {/* Activity Timeline */}
              <div className="card">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  📈 Aktivitas 7 Hari Terakhir
                </h3>
                <ActivityChart data={preferences.activity_timeline} />
              </div>

              {/* Mood Preferences */}
              <div className="card">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  💭 Preferensi Suasana
                </h3>
                <MoodsList data={preferences.preferred_moods} />
              </div>
            </div>

            {/* Recent Searches */}
            <div className="card">
              <h3 className="text-xl font-bold text-gray-800 mb-4">
                🔍 Pencarian Terakhir
              </h3>
              <TopSearchesList data={preferences.top_searches} />
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className="card text-center py-16">
            <div className="text-6xl mb-4">🤖</div>
            <h3 className="text-2xl font-bold text-gray-800 mb-2">
              Belum Ada Riwayat Percakapan
            </h3>
            <p className="text-gray-600 mb-6">
              Mulai chat dengan chatbot untuk mendapatkan rekomendasi restoran yang pas untuk Anda!
            </p>
            <button 
              onClick={() => document.querySelector('.floating-chatbot-trigger')?.click()}
              className="btn-primary"
            >
              Mulai Chat Sekarang
            </button>
          </div>
        )}
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

/**
 * Restaurant Recommendations Component
 * Komponen untuk menampilkan rekomendasi restoran berdasarkan preferensi user
 */
import { useState, useEffect } from 'react';
import { FiFilter, FiSearch, FiMapPin, FiTrendingUp } from 'react-icons/fi';
import RestaurantCard from './RestaurantCard';
import { recommendationsAPI } from '../services/api';

const RestaurantRecommendations = ({ userPreferences }) => {
  const [restaurants, setRestaurants] = useState([]);
  const [filteredRestaurants, setFilteredRestaurants] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [personalizationInfo, setPersonalizationInfo] = useState(null);

  useEffect(() => {
    fetchRecommendations();
  }, [userPreferences]);

  useEffect(() => {
    filterRestaurants();
  }, [restaurants, selectedFilter, searchQuery]);

  const fetchRecommendations = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Pull session context to decide personalization
      const sessionId = localStorage.getItem('session_id');
      const deviceToken = localStorage.getItem('device_token') || `web_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('device_token', deviceToken);

      const params = {
        device_token: deviceToken,
        limit: 100  // Request all restaurants from CSV
      };

      if (sessionId) {
        params.session_id = sessionId;
      }

      const response = await recommendationsAPI.getRecommendations(params);

      if (response.success) {
        const apiRestaurants = response.data?.restaurants || [];
        setRestaurants(apiRestaurants);
        setIsPersonalized(Boolean(response.data?.personalized));
        
        console.log('=== PERSONALIZATION DEBUG ===');
        console.log('Personalized:', response.data?.personalized);
        console.log('Total restaurants:', apiRestaurants.length);
        console.log('First 3 scores:', apiRestaurants.slice(0, 3).map(r => ({
          name: r.name,
          score: r.personalization_score
        })));

        if (apiRestaurants.length === 0) {
          setPersonalizationInfo({
            message: 'Belum ada rekomendasi. Mulai chat untuk mempersonalisasi.',
            icon: '💬'
          });
        } else if (response.data?.personalized) {
          setPersonalizationInfo({
            message: 'Rekomendasi dipersonalisasi dari riwayat Anda',
            icon: '🎯'
          });
        } else {
          setPersonalizationInfo({
            message: 'Menampilkan rekomendasi populer. Chat untuk personalisasi.',
            icon: '✨'
          });
        }
      } else {
        setError('Gagal memuat rekomendasi');
        setRestaurants([]);
        setIsPersonalized(false);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setError('Gagal memuat rekomendasi');
      setRestaurants([]);
      setIsPersonalized(false);
    } finally {
      setIsLoading(false);
    }
  };

  const filterRestaurants = () => {
    let filtered = restaurants;

    // Filter by category
    if (selectedFilter !== 'all') {
      filtered = filtered.filter(restaurant => 
        restaurant.category === selectedFilter
      );
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(restaurant =>
        restaurant.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        restaurant.cuisine.toLowerCase().includes(searchQuery.toLowerCase()) ||
        restaurant.location.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredRestaurants(filtered);
  };

  const handleCardClick = (restaurant) => {
    // Handle restaurant card click - bisa redirect ke detail page
    console.log('Restaurant clicked:', restaurant);
    // Bisa menambahkan logic untuk membuka modal detail atau redirect
  };

  const filterButtons = [
    { key: 'all', label: 'Semua', icon: <FiTrendingUp /> },
    { key: 'indonesian', label: 'Masakan Indonesia', icon: '🍛' },
    { key: 'seafood', label: 'Seafood', icon: '🐟' },
    { key: 'western', label: 'Western', icon: '🍕' },
    { key: 'street_food', label: 'Street Food', icon: '🥘' },
    { key: 'fast_food', label: 'Fast Food', icon: '🍔' }
  ];

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">{error}</h3>
        <p className="text-gray-600 mb-4">Silakan coba lagi atau buka chat untuk meminta rekomendasi.</p>
        <button
          onClick={fetchRecommendations}
          className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
        >
          Muat Ulang
        </button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Memuat rekomendasi...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Results Count and Personalization Info */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
        <div className="flex items-center gap-2">
          <p className="text-gray-600 font-medium">
            {filteredRestaurants.length} Restoran
          </p>
          {isPersonalized && filteredRestaurants.length > 0 && (
            <span className="px-2 py-1 bg-green-50 text-green-700 text-xs font-semibold rounded">
              Diurutkan berdasarkan kecocokan
            </span>
          )}
        </div>
        
        {/* Personalization Indicator */}
        {personalizationInfo && (
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium shadow-sm ${
            isPersonalized 
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-800 border-2 border-green-200' 
              : 'bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-800 border-2 border-blue-200'
          }`}>
            <span className="text-lg">{personalizationInfo.icon}</span>
            <span>{personalizationInfo.message}</span>
          </div>
        )}
      </div>

      {/* Chat Prompt for Non-Personalized */}
      {/* {!isPersonalized && (
        <div className="bg-gradient-to-r from-primary-50 to-primary-100 border border-primary-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="text-2xl">💡</div>
            <div>
              <h3 className="font-semibold text-primary-900 mb-1">
                Dapatkan Rekomendasi yang Lebih Personal
              </h3>
              <p className="text-primary-700 text-sm mb-3">
                Chat dengan bot kami untuk mendapatkan rekomendasi restoran yang sesuai dengan selera Anda
              </p>
              <button 
                onClick={() => document.querySelector('.floating-chatbot-trigger')?.click()}
                className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                Mulai Chat Sekarang
              </button>
            </div>
          </div>
        </div>
      )} */}

      {/* Restaurant Grid */}
      {filteredRestaurants.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRestaurants.map((restaurant, index) => (
            <RestaurantCard
              key={`${restaurant.id}-${restaurant.name}-${index}`}
              restaurant={restaurant}
              onCardClick={handleCardClick}
              isPersonalized={isPersonalized}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Tidak ada hasil ditemukan
          </h3>
          <p className="text-gray-600 mb-4">
            Coba ubah kata kunci pencarian atau filter yang dipilih
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setSelectedFilter('all');
            }}
            className="btn-primary"
          >
            Reset Filter
          </button>
        </div>
      )}
    </div>
  );
};

export default RestaurantRecommendations;
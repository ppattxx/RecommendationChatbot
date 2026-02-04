/**
 * Restaurant Recommendations Component
 * Menampilkan SEMUA restoran dengan Top 5 mendapat label "Pilihan Terbaik"
 * Urutan berdasarkan Cosine Similarity score
 * Data diambil dari endpoint /recommendations/all-ranked
 */
import { useState, useEffect, useCallback } from 'react';
import { FiTrendingUp, FiRefreshCw, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import RestaurantCard from './RestaurantCard';
import { recommendationsAPI } from '../services/api';
import { usePersonalization } from '../contexts/PersonalizationContext';

/**
 * Loading Skeleton untuk card
 */
const CardSkeleton = () => (
  <div className="bg-white rounded-xl shadow-sm p-4 animate-pulse">
    <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
    <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div className="h-4 bg-gray-100 rounded w-1/2 mb-2"></div>
    <div className="h-4 bg-gray-100 rounded w-full mb-2"></div>
    <div className="flex gap-2 mt-3">
      <div className="h-6 bg-gray-100 rounded w-16"></div>
      <div className="h-6 bg-gray-100 rounded w-20"></div>
    </div>
  </div>
);

/**
 * Pagination Component
 */
const Pagination = ({ currentPage, totalPages, onPageChange, isLoading }) => {
  const getPageNumbers = () => {
    const pages = [];
    const showEllipsis = totalPages > 7;
    
    if (!showEllipsis) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      if (currentPage <= 4) {
        for (let i = 1; i <= 5; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 3) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    return pages;
  };

  return (
    <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mt-8">
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1 || isLoading}
          className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <FiChevronLeft className="w-5 h-5" />
        </button>
        
        <div className="flex items-center gap-1">
          {getPageNumbers().map((page, index) => (
            page === '...' ? (
              <span key={`ellipsis-${index}`} className="px-2 py-1 text-gray-400">...</span>
            ) : (
              <button
                key={page}
                onClick={() => onPageChange(page)}
                disabled={isLoading}
                className={`min-w-[36px] h-9 px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  currentPage === page
                    ? 'bg-primary-600 text-white'
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                {page}
              </button>
            )
          ))}
        </div>
        
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages || isLoading}
          className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <FiChevronRight className="w-5 h-5" />
        </button>
      </div>
      
      <span className="text-sm text-gray-500">
        Halaman {currentPage} dari {totalPages}
      </span>
    </div>
  );
};

const RestaurantRecommendations = ({ userPreferences }) => {
  const [restaurants, setRestaurants] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [queryUsed, setQueryUsed] = useState('');
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState({
    totalPages: 1,
    totalItems: 0,
    itemsPerPage: 20,
    hasNext: false,
    hasPrev: false
  });
  
  // Get context for seamless updates
  const { sessionId, deviceToken } = usePersonalization();

  /**
   * Fetch ALL ranked recommendations with pagination
   */
  const fetchAllRankedRecommendations = useCallback(async (page = 1) => {
    try {
      setIsLoading(true);
      setError(null);

      const token = deviceToken || localStorage.getItem('device_token') || `web_${Math.random().toString(36).substr(2, 9)}`;
      if (!localStorage.getItem('device_token')) {
        localStorage.setItem('device_token', token);
      }

      const params = {
        device_token: token,
        page: page,
        limit: 20
      };

      if (sessionId) {
        params.session_id = sessionId;
      }

      // Use ALL-RANKED endpoint with Cosine Similarity sorting
      const response = await recommendationsAPI.getAllRankedRecommendations(params);

      if (response.success && response.data?.restaurants) {
        setRestaurants(response.data.restaurants);
        setIsPersonalized(response.data.personalized || false);
        setQueryUsed(response.data.query || '');
        
        // Update pagination state
        if (response.data.pagination) {
          setPagination({
            totalPages: response.data.pagination.total_pages || 1,
            totalItems: response.data.pagination.total_items || 0,
            itemsPerPage: response.data.pagination.items_per_page || 20,
            hasNext: response.data.pagination.has_next || false,
            hasPrev: response.data.pagination.has_prev || false
          });
        }
        
        console.log('=== ALL RANKED RECOMMENDATIONS ===');
        console.log('Page:', page);
        console.log('Personalized:', response.data.personalized);
        console.log('Query used:', response.data.query);
        console.log('Algorithm:', response.data.algorithm);
        console.log('Restaurants on page:', response.data.restaurants.length);
        console.log('Total items:', response.data.pagination?.total_items);
        
        if (response.data.restaurants.length > 0) {
          const top5OnPage = response.data.restaurants.filter(r => r.is_top5);
          if (top5OnPage.length > 0) {
            console.log('Top 5 on this page:', top5OnPage.map(r => ({
              rank: r.rank,
              name: r.name,
              similarity: r.similarity_score
            })));
          }
        }
      } else {
        setError('Gagal memuat rekomendasi');
        setRestaurants([]);
      }
    } catch (err) {
      console.error('Error fetching all ranked recommendations:', err);
      setError('Gagal memuat rekomendasi');
      setRestaurants([]);
    } finally {
      setIsLoading(false);
    }
  }, [deviceToken, sessionId]);

  // Fetch on mount and when preferences/context changes
  useEffect(() => {
    fetchAllRankedRecommendations(1);
    setCurrentPage(1);
  }, [userPreferences, sessionId, fetchAllRankedRecommendations]);

  // Handle page change
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.totalPages && newPage !== currentPage) {
      setCurrentPage(newPage);
      fetchAllRankedRecommendations(newPage);
      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleCardClick = (restaurant) => {
    console.log('Restaurant clicked:', restaurant);
  };

  // Error state
  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">⚠️</div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">{error}</h3>
        <p className="text-gray-600 mb-4">Silakan coba lagi atau chat untuk mendapatkan rekomendasi.</p>
        <button
          onClick={() => fetchAllRankedRecommendations(currentPage)}
          className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <FiRefreshCw className="w-4 h-4" />
          Muat Ulang
        </button>
      </div>
    );
  }

  // Loading state
  if (isLoading && restaurants.length === 0) {
    return (
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="animate-pulse">
          <div className="h-7 bg-gray-200 rounded w-64 mb-2"></div>
          <div className="h-4 bg-gray-100 rounded w-96"></div>
        </div>
        
        {/* Cards Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <FiTrendingUp className="w-6 h-6 text-primary-600" />
            <h2 className="text-2xl font-bold text-gray-800">
              {isPersonalized ? 'Rekomendasi untuk Anda' : 'Restoran di Lombok'}
            </h2>
          </div>
          <p className="text-gray-600 text-sm">
            {isPersonalized 
              ? `Diurutkan berdasarkan preferensi Anda${queryUsed ? `: ${queryUsed}` : ''}`
              : `${pagination.totalItems.toLocaleString()} restoran tersedia • Diurutkan berdasarkan relevansi`}
          </p>
        </div>
        
        {/* Personalization Badge */}
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium ${
            isPersonalized 
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-800 border border-green-200' 
              : 'bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-800 border border-blue-200'
          }`}>
            <span>{isPersonalized ? '🎯 Personal' : '⭐ Semua Restoran'}</span>
          </div>
          
          <button
            onClick={() => fetchAllRankedRecommendations(currentPage)}
            disabled={isLoading}
            className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-50 transition-colors"
            title="Refresh"
          >
            <FiRefreshCw className={`w-5 h-5 text-gray-600 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Restaurant Grid - All Restaurants, Top 5 with special label */}
      {restaurants.length > 0 ? (
        <>
          <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 ${isLoading ? 'opacity-60' : ''}`}>
            {restaurants.map((restaurant) => (
              <RestaurantCard
                key={`${restaurant.id}-${restaurant.rank}`}
                restaurant={{
                  ...restaurant,
                  // Map similarity_score to personalization_score for card display
                  personalization_score: restaurant.similarity_score * 10
                }}
                onCardClick={handleCardClick}
                isPersonalized={isPersonalized}
                // ONLY show rank for Top 5 (is_top5 flag from backend)
                showRank={restaurant.is_top5}
              />
            ))}
          </div>
          
          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <Pagination
              currentPage={currentPage}
              totalPages={pagination.totalPages}
              onPageChange={handlePageChange}
              isLoading={isLoading}
            />
          )}
        </>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Belum ada restoran
          </h3>
          <p className="text-gray-600 mb-4">
            Chat dengan bot untuk mendapatkan rekomendasi yang sesuai dengan preferensi Anda
          </p>
        </div>
      )}

      {/* Algorithm Info */}
      <div className="text-center text-xs text-gray-400 pt-4 border-t border-gray-100">
        Dihitung menggunakan Cosine Similarity • Top 5 ditandai dengan label "Pilihan Terbaik" • Tie-breaker: Rating & Review Count
      </div>
    </div>
  );
};

export default RestaurantRecommendations;
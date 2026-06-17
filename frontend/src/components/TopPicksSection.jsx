/**
 * TopPicksSection Component
 * Displays trending/popular restaurants in a TripGO-style card grid.
 * Uses the /recommendations/trending endpoint with fallback to /recommendations/all-ranked.
 */
import { useState, useEffect, useCallback } from 'react';
import RestaurantCard from './RestaurantCard';
import { recommendationsAPI } from '../services/api';
import { usePersonalization } from '../contexts/PersonalizationContext';

const FILTER_CHIPS = [
  { key: 'all', label: 'Semua', icon: '🔥' },
  { key: 'senggigi', label: 'Senggigi', icon: '🏖️' },
  { key: 'kuta', label: 'Kuta', icon: '🌊' },
  { key: 'mataram', label: 'Mataram', icon: '🏙️' },
  { key: 'gili', label: 'Gili', icon: '🏝️' },
];

const CardSkeleton = () => (
  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden animate-pulse">
    <div className="h-52 bg-gray-100" />
    <div className="p-5 space-y-3">
      <div className="h-5 bg-gray-100 rounded-lg w-3/4" />
      <div className="h-4 bg-gray-50 rounded-lg w-1/2" />
      <div className="flex gap-2">
        <div className="h-6 bg-gray-50 rounded-full w-20" />
        <div className="h-6 bg-gray-50 rounded-full w-16" />
      </div>
      <div className="h-9 bg-gray-50 rounded-xl w-full mt-2" />
    </div>
  </div>
);

const TopPicksSection = ({ onViewDetail }) => {
  const [restaurants, setRestaurants] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;
  const { deviceToken, sessionId, preferences, personalizationVersion, latestUserQuery } = usePersonalization();

  const fetchRestaurants = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = deviceToken || localStorage.getItem('device_token');
      const pageSize = 100;
      const allRows = [];
      let currentPage = 1;
      let hasMore = true;

      // Fetch ALL pages (no limit, allows full 1163 restaurant dataset)
      do {
        const params = {
          device_token: token,
          page: currentPage,
          limit: pageSize,
        };
        if (sessionId) params.session_id = sessionId;
        
        // Pass latest user query so backend can rank consistently with chatbot
        if (latestUserQuery && latestUserQuery.trim()) {
          params.query = latestUserQuery.trim();
        }

        const response = await recommendationsAPI.getAllRankedRecommendations(params);
        if (!(response.success && response.data?.restaurants)) {
          break;
        }

        allRows.push(...response.data.restaurants);
        
        // Check if there are more pages
        hasMore = response.data.pagination?.has_next || false;
        currentPage += 1;
      } while (hasMore);

      setRestaurants(allRows);

      if (allRows.length === 0) {
        setError('Data restoran kosong');
      }
    } catch (err) {
      console.error('Error fetching restaurants:', err);
      setError('Gagal memuat data restoran');
      setRestaurants([]);
    } finally {
      setIsLoading(false);
    }
  }, [deviceToken, sessionId, latestUserQuery]);

  useEffect(() => {
    fetchRestaurants();
  }, [fetchRestaurants, personalizationVersion]);

  // Filter restaurants by location chip
  const filteredRestaurants = activeFilter === 'all'
    ? restaurants
    : restaurants.filter((r) => {
        const location = (r.location || r.entitas_lokasi || '').toLowerCase();
        return location.includes(activeFilter);
      });

  const totalPages = Math.max(Math.ceil(filteredRestaurants.length / itemsPerPage), 1);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const displayRestaurants = filteredRestaurants.slice(startIndex, startIndex + itemsPerPage);

  useEffect(() => {
    setCurrentPage(1);
  }, [activeFilter, restaurants.length]);

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  const pageNumbers = [];
  for (let i = 1; i <= totalPages; i += 1) {
    pageNumbers.push(i);
  }

  return (
    <section id="top-picks" className="section-padding bg-gray-50/50">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12 space-y-4">
          <h2 className="text-3xl sm:text-4xl font-bold font-poppins text-gray-900">
            Restoran Populer di{' '}
            <span className="gradient-text">Lombok</span>
          </h2>
        </div>

        {/* Error */}
        {error && (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">{error}</p>
            <button
              onClick={fetchRestaurants}
              className="btn-primary text-sm py-2.5 px-6"
            >
              Coba Lagi
            </button>
          </div>
        )}

        {/* Loading */}
        {isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Cards Grid */}
        {!isLoading && !error && displayRestaurants.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {displayRestaurants.map((restaurant, index) => (
                <div
                  key={restaurant.id || `${restaurant.name}-${index}`}
                  className="animate-fade-in"
                  style={{ animationDelay: `${index * 80}ms`, animationFillMode: 'backwards' }}
                >
                  <RestaurantCard
                    restaurant={restaurant}
                    onCardClick={() => onViewDetail && onViewDetail(restaurant)}
                    isPersonalized={Boolean(preferences)}
                    showRank={false}
                  />
                </div>
              ))}
            </div>

            {totalPages > 1 && (
              <div className="mt-10 flex flex-col items-center gap-3">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-2 rounded-lg border border-gray-200 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Sebelumnya
                  </button>

                  <div className="flex items-center gap-1 flex-wrap justify-center">
                    {pageNumbers.slice(Math.max(0, currentPage - 3), Math.min(totalPages, currentPage + 2)).map((n) => (
                      <button
                        key={n}
                        onClick={() => setCurrentPage(n)}
                        className={`w-9 h-9 rounded-lg text-sm font-medium ${
                          n === currentPage
                            ? 'bg-primary-600 text-white'
                            : 'border border-gray-200 hover:bg-gray-50 text-gray-700'
                        }`}
                      >
                        {n}
                      </button>
                    ))}
                  </div>

                  <button
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-2 rounded-lg border border-gray-200 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Berikutnya
                  </button>
                </div>

                <p className="text-xs text-gray-500">
                  Halaman {currentPage} dari {totalPages}
                </p>
              </div>
            )}
          </>
        )}

        {/* Empty state */}
        {!isLoading && !error && displayRestaurants.length === 0 && (
          <div className="text-center py-16">
            <span className="text-5xl block mb-4">🔍</span>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              {activeFilter !== 'all'
                ? `Belum ada restoran di ${activeFilter}`
                : 'Belum ada data restoran'}
            </h3>
            <p className="text-gray-500 text-sm">
              Chat dengan AI untuk mendapatkan rekomendasi personal
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default TopPicksSection;

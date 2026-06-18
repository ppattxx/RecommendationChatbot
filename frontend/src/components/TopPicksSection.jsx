import { useCallback, useEffect, useState } from 'react';
import { FiChevronLeft, FiChevronRight, FiMapPin, FiRefreshCw, FiSearch } from 'react-icons/fi';
import RestaurantCard from './RestaurantCard';
import { recommendationsAPI } from '../services/api';
import { usePersonalization } from '../contexts/PersonalizationContext';


const CardSkeleton = () => (
  <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm animate-pulse">
    <div className="h-56 bg-slate-200" />
    <div className="space-y-4 p-5">
      <div className="h-5 w-3/4 rounded-lg bg-slate-200" />
      <div className="h-4 w-1/2 rounded-lg bg-slate-100" />
      <div className="grid grid-cols-2 gap-2">
        <div className="h-8 rounded-xl bg-slate-100" />
        <div className="h-8 rounded-xl bg-slate-100" />
      </div>
      <div className="h-10 rounded-xl bg-slate-100" />
    </div>
  </div>
);

const TopPicksSection = ({ onViewDetail }) => {
  const [restaurants, setRestaurants] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
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
      let apiPage = 1;
      let hasMore = true;

      do {
        const params = {
          device_token: token,
          page: apiPage,
          limit: pageSize,
        };
        if (sessionId) params.session_id = sessionId;
        if (latestUserQuery && latestUserQuery.trim()) params.query = latestUserQuery.trim();

        const response = await recommendationsAPI.getAllRankedRecommendations(params);
        if (!(response.success && response.data?.restaurants)) break;

        allRows.push(...response.data.restaurants);
        hasMore = response.data.pagination?.has_next || false;
        apiPage += 1;
      } while (hasMore);

      setRestaurants(allRows);
      if (allRows.length === 0) setError('Data restoran kosong');
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


  const filteredRestaurants = restaurants;

  const totalPages = Math.max(Math.ceil(filteredRestaurants.length / itemsPerPage), 1);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const displayRestaurants = filteredRestaurants.slice(startIndex, startIndex + itemsPerPage);


  useEffect(() => {
    setCurrentPage(1);
  }, [restaurants.length]);

  useEffect(() => {
    if (currentPage > totalPages) setCurrentPage(totalPages);
  }, [currentPage, totalPages]);

  const pageNumbers = [];
  for (let i = 1; i <= totalPages; i += 1) pageNumbers.push(i);

  return (
    <section id="top-picks" className="bg-slate-50 px-4 py-16 sm:px-6 md:py-24 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-10 grid gap-6 lg:grid-cols-[0.95fr_1.05fr] lg:items-end">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full bg-primary-50 px-3 py-1.5 text-xs font-bold uppercase tracking-[0.16em] text-primary-700 ring-1 ring-primary-100">
              <FiMapPin className="h-4 w-4" />
              Lombok food map
            </span>
            <h2 className="mt-4 font-poppins text-3xl font-extrabold leading-tight text-slate-950 sm:text-4xl lg:text-5xl">
              Tempat makan yang masuk akal untuk rute perjalanan Anda.
            </h2>
          </div>
          <p className="max-w-2xl text-sm leading-7 text-slate-600 sm:text-base lg:justify-self-end">
            Buka detail restoran untuk membaca lokasi, kisaran harga, dan informasi penting sebelum berangkat. Rekomendasi akan ikut menyesuaikan percakapan Anda dengan Traveler.
          </p>
        </div>

        <div className="mb-8 flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-bold text-slate-900">Semua rekomendasi restoran</p>
            <p className="mt-1 text-xs leading-5 text-slate-500">Diurutkan berdasarkan relevansi dan preferensi percakapan Traveler.</p>
          </div>

          <div className="flex items-center justify-between gap-3 sm:justify-end">
            <span className="rounded-xl bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-500">
              {filteredRestaurants.length.toLocaleString('id-ID')} restoran
            </span>
            <button
              onClick={fetchRestaurants}
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition hover:border-primary-200 hover:bg-primary-50 hover:text-primary-700"
              title="Muat ulang"
            >
              <FiRefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-2xl border border-orange-100 bg-orange-50 p-8 text-center">
            <p className="mb-4 font-semibold text-orange-900">{error}</p>
            <button onClick={fetchRestaurants} className="btn-primary text-sm">
              Coba Lagi
            </button>
          </div>
        )}

        {isLoading && (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((item) => (
              <CardSkeleton key={item} />
            ))}
          </div>
        )}

        {!isLoading && !error && displayRestaurants.length > 0 && (
          <>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {displayRestaurants.map((restaurant, index) => (
                <div
                  key={restaurant.id || `${restaurant.name}-${index}`}
                  className="animate-fade-in"
                  style={{ animationDelay: `${index * 60}ms`, animationFillMode: 'backwards' }}
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
                <div className="flex max-w-full items-center gap-2 overflow-x-auto rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
                  <button
                    onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                    disabled={currentPage === 1}
                    className="flex h-10 min-w-10 items-center justify-center rounded-xl text-slate-600 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <FiChevronLeft className="h-5 w-5" />
                  </button>

                  {pageNumbers.slice(Math.max(0, currentPage - 3), Math.min(totalPages, currentPage + 2)).map((number) => (
                    <button
                      key={number}
                      onClick={() => setCurrentPage(number)}
                      className={`h-10 min-w-10 rounded-xl px-3 text-sm font-bold transition ${
                        number === currentPage
                          ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20'
                          : 'text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      {number}
                    </button>
                  ))}

                  <button
                    onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
                    disabled={currentPage === totalPages}
                    className="flex h-10 min-w-10 items-center justify-center rounded-xl text-slate-600 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <FiChevronRight className="h-5 w-5" />
                  </button>
                </div>
                <p className="text-xs font-medium text-slate-500">
                  Halaman {currentPage} dari {totalPages}
                </p>
              </div>
            )}
          </>
        )}

        {!isLoading && !error && displayRestaurants.length === 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
              <FiSearch className="h-6 w-6" />
            </div>
            <h3 className="font-poppins text-xl font-bold text-slate-900">
              Belum ada data restoran
</h3>
            <p className="mt-2 text-sm text-slate-500">
              Chat dengan Traveler untuk mendapatkan rekomendasi personal berdasarkan rute dan selera.
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default TopPicksSection;





import { useEffect } from 'react';

const RestaurantDetailModal = ({ restaurant, onClose }) => {
  // Prevent body scroll when modal is open
  useEffect(() => {
    if (restaurant) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [restaurant]);

  if (!restaurant) return null;

  // The chat parser currently only yields basic data, but top picks / API gives full data.
  // We'll prepare to show comprehensive data if available, with fallbacks for chat parsed data.
  const name = restaurant.name || 'Unknown Restaurant';
  const rating = restaurant.rating || 0;
  const description = restaurant.about || restaurant.description || 'Tidak ada deskripsi.';
  const images = [restaurant.image_url, restaurant.img2_url, restaurant.img3_url].filter(Boolean);
  const cuisines = restaurant.cuisines_list || (restaurant.cuisine ? restaurant.cuisine.split(', ') : []);
  const features = restaurant.features || [];
  const schedule = restaurant.schedule || {};
  const priceRange = restaurant.price_range || '$$';
  const address = restaurant.address || restaurant.location || 'Lombok';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/40 backdrop-blur-sm animate-fade-in">
      <div 
        className="bg-white rounded-3xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl flex flex-col md:flex-row animate-scale-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Left Column: Images */}
        <div className="md:w-5/12 bg-gray-100 flex flex-col relative h-64 md:h-auto">
          {images.length > 0 ? (
            <div className="h-full flex flex-col gap-1 p-1">
              <div className="flex-1 rounded-2xl overflow-hidden relative group">
                <img src={images[0]} alt={name} className="w-full h-full object-cover transition duration-700 group-hover:scale-110" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </div>
              {images.length > 1 && (
                <div className="flex gap-1 h-1/3">
                  {images.slice(1, 3).map((img, i) => (
                    <div key={i} className="flex-1 rounded-xl overflow-hidden relative">
                      <img src={img} alt={`${name} detail ${i}`} className="w-full h-full object-cover" />
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              🖼️ Tidak ada gambar
            </div>
          )}
          
          <button 
            onClick={onClose}
            className="absolute top-4 left-4 bg-white/80 backdrop-blur-md text-gray-800 p-2 rounded-full shadow-sm hover:bg-white md:hidden"
          >
            ✕
          </button>
        </div>

        {/* Right Column: Content */}
        <div className="md:w-7/12 overflow-y-auto w-full">
          <div className="p-6 md:p-8 space-y-6">
            
            {/* Header */}
            <div>
              <div className="flex justify-between items-start mb-2">
                <h2 className="text-3xl font-bold text-gray-900 font-poppins">{name}</h2>
                <button 
                  onClick={onClose}
                  className="hidden md:flex bg-gray-100 text-gray-500 hover:bg-gray-200 p-2 rounded-full transition-colors"
                >
                  ✕
                </button>
              </div>
              
              <div className="flex items-center gap-4 text-sm text-gray-600 font-medium">
                <div className="flex items-center gap-1.5 px-2.5 py-1 bg-yellow-50 text-yellow-700 rounded-lg">
                  <span className="text-yellow-500">★</span> {rating}
                </div>
                <div className="flex items-center gap-1 bg-green-50 text-green-700 px-2.5 py-1 rounded-lg">
                  <span className="text-green-600">💰</span> {priceRange}
                </div>
              </div>
            </div>

            {/* Badges / Cuisines */}
            {cuisines.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {cuisines.map((c, i) => (
                  <span key={i} className="bg-primary-50 text-primary-700 px-3 py-1 rounded-full text-sm font-medium border border-primary-100">
                    🍽️ {c}
                  </span>
                ))}
              </div>
            )}

            {/* About */}
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-gray-800 font-poppins">Tentang Restoran</h3>
              <p className="text-gray-600 leading-relaxed text-sm md:text-base">
                {description}
              </p>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-gray-50 border border-gray-100 p-4 rounded-2xl">
              
              {/* Address */}
              <div className="space-y-1">
                <span className="text-xs text-gray-500 font-bold uppercase tracking-wider">Lokasi</span>
                <p className="text-sm font-medium text-gray-800">{address}</p>
              </div>

              {/* Hours (Today) */}
              <div className="space-y-1">
                <span className="text-xs text-gray-500 font-bold uppercase tracking-wider">Jam Buka (Hari Ini)</span>
                <p className="text-sm font-medium text-gray-800">
                  {restaurant.opening_hours || 'Hubungi untuk jadwal'}
                </p>
              </div>
            </div>

            {/* Features (if available) */}
            {features && features.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-800 font-poppins">Fasilitas</h3>
                <div className="grid grid-cols-2 gap-3 text-sm text-gray-600">
                  {features.map((f, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary-500"></div>
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Full Schedule Map (if available) */}
            {Object.keys(schedule).length > 0 && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-800 font-poppins">Jam Operasional</h3>
                <div className="bg-white border border-gray-100 rounded-xl overflow-hidden divide-y divide-gray-50 text-sm">
                  {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map(day => {
                    const idDay = {
                      monday: 'Senin', tuesday: 'Selasa', wednesday: 'Rabu', 
                      thursday: 'Kamis', friday: 'Jumat', saturday: 'Sabtu', sunday: 'Minggu'
                    }[day];
                    return (
                      <div key={day} className="flex justify-between px-4 py-2 hover:bg-gray-50 transition-colors">
                        <span className="text-gray-500 font-medium">{idDay}</span>
                        <span className="text-gray-900">{schedule[day] || 'Tutup'}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default RestaurantDetailModal;

/**
 * RestaurantCard Component — TripGO-Inspired Redesign
 * Card untuk menampilkan informasi restoran dengan visual premium.
 * Mendukung: rating stars, location/cuisine badges, price range, rank badge.
 */
import { FiMapPin, FiStar, FiDollarSign, FiClock } from 'react-icons/fi';

const RestaurantCard = ({ restaurant, onCardClick, isPersonalized, showRank = false }) => {
  const {
    name,
    location,
    rating,
    price_range,
    cuisine,
    cuisines,
    image_url,
    img1_url,
    img,
    image,
    description,
    about,
    opening_hours,
    popular_dishes,
    rank,
  } = restaurant;

  const displayCuisine = cuisine || cuisines || '';
  const displayDescription = description || about || '';
  const imageCandidates = [image_url, img1_url, img, image];
  const displayImage = imageCandidates.find((url) => {
    if (!url) return false;
    const u = String(url).trim();
    return u.length > 0 && u.toLowerCase() !== 'nan';
  });

  // Rating stars
  const renderStars = (r) => {
    if (!r || isNaN(r)) return null;
    const numRating = parseFloat(r);
    return (
      <div className="flex items-center gap-0.5">
        {[...Array(5)].map((_, i) => (
          <svg
            key={i}
            className={`w-4 h-4 ${
              i < Math.floor(numRating) ? 'text-yellow-400' : 'text-gray-200'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    );
  };

  // Price indicators
  const renderPriceRange = (price) => {
    const priceLevel = price?.toLowerCase() || '';
    let dollarCount = 1;
    if (priceLevel.includes('$$') && !priceLevel.includes('$$$')) dollarCount = 2;
    if (priceLevel.includes('$$$') || priceLevel.includes('mahal') || priceLevel.includes('premium')) dollarCount = 3;
    if (priceLevel.includes('menengah') || priceLevel.includes('medium')) dollarCount = 2;

    return (
      <div className="flex items-center">
        {Array.from({ length: 3 }, (_, i) => (
          <FiDollarSign
            key={i}
            className={`w-3 h-3 ${i < dollarCount ? 'text-emerald-500' : 'text-gray-200'}`}
          />
        ))}
      </div>
    );
  };

  // Format cuisine for badge
  const cuisineBadge = () => {
    if (!displayCuisine) return null;
    let text = String(displayCuisine);
    // Remove brackets and quotes from Python list format
    text = text.replace(/[\[\]']/g, '').trim();
    // Take first cuisine only for badge
    const first = text.split(',')[0].trim();
    return first.length > 18 ? first.slice(0, 18) + '…' : first;
  };

  return (
    <div
      className={`group bg-white rounded-2xl overflow-hidden border border-gray-100 hover:border-primary-100 
        shadow-sm hover:shadow-xl hover:shadow-primary-600/5 transition-all duration-500 cursor-pointer 
        transform hover:-translate-y-1 relative ${
        showRank ? 'ring-2 ring-primary-300/60' : ''
      }`}
      onClick={() => onCardClick?.(restaurant)}
    >
      {/* Rank Badge */}
      {showRank && rank && (
        <div className="absolute top-3 left-3 z-10 flex items-center gap-1.5">
          <div
            className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-white text-sm shadow-lg ${
              rank === 1
                ? 'bg-gradient-to-br from-yellow-400 to-amber-500'
                : rank === 2
                ? 'bg-gradient-to-br from-gray-300 to-gray-400'
                : rank === 3
                ? 'bg-gradient-to-br from-amber-500 to-amber-600'
                : 'bg-gradient-to-br from-primary-500 to-primary-700'
            }`}
          >
            #{rank}
          </div>
          <span className="px-2 py-1 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[10px] font-bold rounded-lg shadow-md">
            Top Pick
          </span>
        </div>
      )}

      {/* Image Container */}
      <div className="relative h-52 overflow-hidden bg-gray-100">
        <img
          src={
            displayImage ||
            `https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=240&fit=crop&crop=center`
          }
          alt={name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
          loading="lazy"
          onError={(e) => {
            e.target.src =
              'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=240&fit=crop&crop=center';
          }}
        />

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent" />

        {/* Favorite button */}
        <button
          className="absolute top-3 right-3 p-2 bg-white/90 hover:bg-white rounded-xl shadow-sm transition-all hover:scale-110"
          onClick={(e) => e.stopPropagation()}
        >
          <svg className="w-4 h-4 text-gray-400 hover:text-red-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </button>

        {/* Cuisine badge on image */}
        {cuisineBadge() && (
          <div className="absolute bottom-3 left-3">
            <span className="px-3 py-1.5 bg-white/95 backdrop-blur-sm text-gray-800 text-xs font-semibold rounded-lg shadow-sm">
              🍽️ {cuisineBadge()}
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5">
        {/* Name & Rating */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <h3 className="text-base font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-1 font-poppins">
            {name}
          </h3>
          <div className="flex items-center gap-1 shrink-0">
            <FiStar className="w-4 h-4 text-yellow-400 fill-current" />
            <span className="text-sm font-bold text-gray-800">{rating || '—'}</span>
          </div>
        </div>

        {/* Location */}
        {location && (
          <div className="flex items-center text-gray-500 mb-3">
            <FiMapPin className="w-3.5 h-3.5 mr-1.5 text-primary-400 shrink-0" />
            <span className="text-sm line-clamp-1">{location}</span>
          </div>
        )}

        {/* Description */}
        {displayDescription && (
          <p className="text-gray-400 text-sm mb-3 line-clamp-2 leading-relaxed">
            {String(displayDescription).length > 100
              ? String(displayDescription).slice(0, 100) + '...'
              : String(displayDescription)}
          </p>
        )}

        {/* Popular Dishes */}
        {popular_dishes && popular_dishes.length > 0 && (
          <div className="mb-3">
            <div className="flex flex-wrap gap-1.5">
              {popular_dishes.slice(0, 3).map((dish, index) => (
                <span
                  key={index}
                  className="px-2.5 py-1 bg-gray-50 text-gray-600 text-[11px] rounded-lg font-medium"
                >
                  {dish}
                </span>
              ))}
              {popular_dishes.length > 3 && (
                <span className="px-2.5 py-1 bg-gray-50 text-gray-400 text-[11px] rounded-lg">
                  +{popular_dishes.length - 3}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Bottom: Price & Hours */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-50">
          <div className="flex items-center gap-1.5">
            {renderPriceRange(price_range)}
            {price_range && (
              <span className="text-xs text-gray-500 ml-0.5">{price_range}</span>
            )}
          </div>

          {opening_hours && (
            <div className="flex items-center text-gray-400">
              <FiClock className="w-3 h-3 mr-1" />
              <span className="text-[11px]">{opening_hours}</span>
            </div>
          )}
        </div>

        {/* CTA Button */}
        <button
          className="w-full mt-4 py-2.5 text-sm font-semibold text-primary-600 bg-primary-50 hover:bg-primary-600 hover:text-white border border-primary-100 hover:border-primary-600 rounded-xl transition-all duration-300"
          onClick={(e) => {
            e.stopPropagation();
            if (onCardClick) onCardClick(restaurant);
          }}
        >
          Lihat Detail
        </button>
      </div>
    </div>
  );
};

export default RestaurantCard;
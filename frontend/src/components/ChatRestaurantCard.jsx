/**
 * ChatRestaurantCard Component
 * Compact card for rendering restaurant recommendations inside chat bubbles.
 */

const ChatRestaurantCard = ({ restaurant, onViewDetail }) => {
  const { name, rating, matchPercentage, cuisine, location, priceRange, isPreferred } = restaurant;

  const renderStars = (r) => {
    if (!r) return null;
    return (
      <div className="flex items-center gap-0.5">
        {[...Array(5)].map((_, i) => (
          <svg
            key={i}
            className={`w-3.5 h-3.5 ${
              i < Math.floor(r)
                ? 'text-yellow-400'
                : i < r
                ? 'text-yellow-300'
                : 'text-gray-200'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
        <span className="text-xs text-gray-500 ml-1 font-medium">{r.toFixed(1)}</span>
      </div>
    );
  };

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-3.5 shadow-sm hover:shadow-md transition-shadow mb-2 max-w-[280px]">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <h4 className="text-sm font-semibold text-gray-900 leading-tight line-clamp-1">
          {name}
        </h4>
        {isPreferred && (
          <span className="shrink-0 text-[9px] bg-green-50 text-green-700 border border-green-200 rounded-full px-1.5 py-0.5 font-bold whitespace-nowrap">
            ✨ Match
          </span>
        )}
      </div>

      {/* Rating & Match */}
      <div className="flex items-center justify-between mb-2.5">
        {renderStars(rating)}
        {matchPercentage && (
          <span className="text-[10px] font-bold text-primary-600 bg-primary-50 rounded-full px-2 py-0.5">
            {matchPercentage}%
          </span>
        )}
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {location && (
          <span className="badge-pill bg-blue-50 text-blue-700 border border-blue-100 text-[10px]">
            📍 {location}
          </span>
        )}
        {cuisine && (
          <span className="badge-pill bg-orange-50 text-orange-700 border border-orange-100 text-[10px]">
            🍽️ {cuisine.length > 20 ? cuisine.slice(0, 20) + '…' : cuisine}
          </span>
        )}
        {priceRange && (
          <span className="badge-pill bg-emerald-50 text-emerald-700 border border-emerald-100 text-[10px]">
            💰 {priceRange}
          </span>
        )}
      </div>

      {/* CTA */}
      <button
        onClick={() => onViewDetail?.(restaurant)}
        className="w-full text-center text-xs font-semibold text-primary-600 hover:text-white bg-primary-50 hover:bg-primary-600 border border-primary-100 hover:border-primary-600 rounded-lg py-2 transition-all duration-200"
      >
        Lihat Detail →
      </button>
    </div>
  );
};

export default ChatRestaurantCard;

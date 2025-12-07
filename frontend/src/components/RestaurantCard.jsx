/**
 * Restaurant Card Component
 * Card untuk menampilkan informasi restoran dengan rating dan foto
 */
import { FiMapPin, FiStar, FiDollarSign, FiClock } from 'react-icons/fi';

const RestaurantCard = ({ restaurant, onCardClick, isPersonalized }) => {
  const {
    name,
    location,
    rating,
    price_range,
    cuisine,
    image_url,
    description,
    opening_hours,
    popular_dishes,
    personalization_score
  } = restaurant;
  
  // Debug personalization
  if (personalization_score > 0) {
    console.log(`${name}: isPersonalized=${isPersonalized}, score=${personalization_score}`);
  }

  // Generate rating stars
  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    const stars = [];

    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <FiStar key={i} className="w-4 h-4 fill-current text-yellow-400" />
      );
    }

    if (hasHalfStar) {
      stars.push(
        <div key="half" className="relative">
          <FiStar className="w-4 h-4 text-gray-300" />
          <div className="absolute inset-0 overflow-hidden w-1/2">
            <FiStar className="w-4 h-4 fill-current text-yellow-400" />
          </div>
        </div>
      );
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <FiStar key={`empty-${i}`} className="w-4 h-4 text-gray-300" />
      );
    }

    return stars;
  };

  // Generate price indicators
  const renderPriceRange = (price) => {
    const priceLevel = price?.toLowerCase();
    let dollarCount = 1;
    
    if (priceLevel?.includes('menengah') || priceLevel?.includes('medium')) dollarCount = 2;
    if (priceLevel?.includes('mahal') || priceLevel?.includes('tinggi') || priceLevel?.includes('premium')) dollarCount = 3;
    
    return Array.from({ length: 3 }, (_, i) => (
      <FiDollarSign 
        key={i} 
        className={`w-3 h-3 ${i < dollarCount ? 'text-green-500' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div 
      className={`bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer group ${
        isPersonalized && personalization_score > 0 
          ? 'ring-2 ring-green-400 ring-opacity-50 hover:ring-green-500 hover:ring-opacity-75' 
          : ''
      }`}
      onClick={() => onCardClick && onCardClick(restaurant)}
    >
      {/* Image */}
      <div className="relative h-48 overflow-hidden">
        <img
          src={image_url || `https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=200&fit=crop&crop=center`}
          alt={name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            e.target.src = `https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=200&fit=crop&crop=center`;
          }}
        />
        
        {/* Personalization Badge */}
        {isPersonalized && personalization_score > 0 && (
          <div className="absolute top-3 left-3">
            <span className="px-3 py-1.5 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-xs font-bold rounded-full flex items-center gap-1 shadow-lg animate-pulse">
              {personalization_score >= 5 ? 'Sangat Cocok!' : 'Cocok untuk Anda'}
            </span>
          </div>
        )}
        
        {/* Score Badge for high matches */}
        {isPersonalized && personalization_score >= 5 && (
          <div className="absolute top-14 left-3">
            <span className="px-2 py-1 bg-yellow-400 text-yellow-900 text-xs font-bold rounded-full flex items-center gap-1 shadow-md">
              {Math.round(personalization_score * 10)}% Match
            </span>
          </div>
        )}
        
        {/* Save to favorites button */}
        <button className="absolute top-3 right-3 p-2 bg-white/80 hover:bg-white rounded-full transition-colors">
          <svg className="w-4 h-4 text-gray-600 hover:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </button>

        {/* Cuisine Badge */}
        {cuisine && (
          <div className="absolute bottom-3 left-3">
            <span className="px-2 py-1 bg-black/70 text-white text-xs rounded-full">
              {cuisine}
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title and Rating */}
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold text-gray-800 group-hover:text-primary-600 transition-colors line-clamp-1">
            {name}
          </h3>
          <div className="flex items-center gap-1 ml-2">
            <span className="text-sm font-medium text-gray-700">{rating}</span>
            <div className="flex">
              {renderStars(rating)}
            </div>
          </div>
        </div>

        {/* Location */}
        <div className="flex items-center text-gray-600 mb-2">
          <FiMapPin className="w-4 h-4 mr-1 flex-shrink-0" />
          <span className="text-sm line-clamp-1">{location}</span>
        </div>

        {/* Description */}
        {description && (
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">
            {description}
          </p>
        )}

        {/* Popular Dishes */}
        {popular_dishes && popular_dishes.length > 0 && (
          <div className="mb-3">
            <span className="text-xs text-gray-500 uppercase tracking-wide">Popular:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {popular_dishes.slice(0, 3).map((dish, index) => (
                <span 
                  key={index} 
                  className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                >
                  {dish}
                </span>
              ))}
              {popular_dishes.length > 3 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                  +{popular_dishes.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Bottom Info */}
        <div className="flex justify-between items-center text-sm">
          {/* Price Range */}
          <div className="flex items-center">
            {renderPriceRange(price_range)}
            <span className="ml-1 text-gray-600">{price_range}</span>
          </div>

          {/* Opening Hours */}
          {opening_hours && (
            <div className="flex items-center text-gray-600">
              <FiClock className="w-3 h-3 mr-1" />
              <span className="text-xs">{opening_hours}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RestaurantCard;
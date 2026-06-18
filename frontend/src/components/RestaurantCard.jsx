import { FiHeart, FiMapPin, FiMessageCircle, FiStar } from 'react-icons/fi';
import { FaWallet } from 'react-icons/fa';

const fallbackImages = [
  'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80',
];

const cleanText = (value) => String(value || '').replace(/[\[\]']/g, '').trim();

const getImageUrl = (...candidates) =>
  candidates.find((url) => {
    if (!url) return false;
    const normalized = String(url).trim();
    return normalized.length > 0 && normalized.toLowerCase() !== 'nan';
  });

const getCuisineLabel = (cuisine, cuisines) => {
  const displayCuisine = cleanText(cuisine || cuisines);
  return displayCuisine.split(',')[0]?.trim();
};

const getOpenStatus = (restaurant) => {
  const explicitStatus = restaurant.open_status || restaurant.status || restaurant.opening_status || restaurant.is_open;
  const hours = restaurant.opening_hours || restaurant.hours_today || restaurant.today_hours;
  const normalized = String(explicitStatus ?? hours ?? '').toLowerCase();

  if (explicitStatus === true || normalized.includes('open')) return { label: 'OPEN', isOpen: true };
  if (explicitStatus === false || normalized.includes('closed') || normalized.includes('tutup')) {
    return { label: 'CLOSED', isOpen: false };
  }

  return { label: 'OPEN', isOpen: true };
};

const getPriceLabel = (priceRange) => {
  const normalized = String(priceRange || '').toLowerCase();

  if (normalized.includes('$$$') || normalized.includes('mahal') || normalized.includes('premium') || normalized.includes('pricey')) {
    return 'Rp Pricey';
  }

  if (normalized.includes('$$') || normalized.includes('menengah') || normalized.includes('medium') || normalized.includes('mid')) {
    return 'Rp Mid';
  }

  return 'Rp Cheap';
};

const StarRating = ({ rating }) => {
  const numericRating = rating && !Number.isNaN(Number(rating)) ? Number(rating) : null;

  if (!numericRating) {
    return <span className="text-sm font-semibold text-slate-400">Belum ada rating</span>;
  }

  return (
    <div className="flex items-center gap-2" aria-label={`Rating ${numericRating.toFixed(1)} dari 5`}>
      <div className="flex items-center gap-0.5">
        {Array.from({ length: 5 }, (_, index) => {
          const isFilled = index < Math.round(numericRating);

          return (
            <FiStar
              key={index}
              className={`h-4 w-4 ${isFilled ? 'fill-amber-400 text-amber-400' : 'text-slate-200'}`}
              aria-hidden="true"
            />
          );
        })}
      </div>
      <span className="text-sm font-bold text-slate-700">{numericRating.toFixed(1)}</span>
    </div>
  );
};

const RestaurantCard = ({ restaurant, onCardClick, onChatClick, showRank = false }) => {
  const {
    name,
    location,
    rating,
    price_range,
    priceRange,
    cuisine,
    cuisines,
    image_url,
    img1_url,
    img,
    image,
    description,
    about,
    popular_dishes,
    rank,
  } = restaurant;

  const displayImage = getImageUrl(image_url, img1_url, img, image);
  const cuisineLabel = getCuisineLabel(cuisine, cuisines);
  const displayDescription = description || about || '';
  const priceLabel = getPriceLabel(price_range || priceRange);
  const status = getOpenStatus(restaurant);

  const handleChatClick = (event) => {
    event.stopPropagation();

    if (onChatClick) {
      onChatClick(restaurant);
      return;
    }

    window.dispatchEvent(new CustomEvent('openRestaurantChat', { detail: restaurant }));
  };

  return (
    <article
      className={`group relative flex h-full w-full cursor-pointer flex-col overflow-hidden rounded-2xl border bg-white shadow-md shadow-slate-900/10 transition duration-300 hover:-translate-y-1.5 hover:shadow-2xl hover:shadow-slate-900/15 ${
        showRank ? 'border-primary-200 ring-2 ring-primary-100' : 'border-slate-200 hover:border-primary-200'
      }`}
      onClick={() => onCardClick?.(restaurant)}
    >
      {showRank && rank && (
        <div className="absolute left-3 top-3 z-20 flex items-center gap-2">
          <span className="rounded-xl bg-primary-600 px-3 py-2 text-xs font-extrabold text-white shadow-lg shadow-primary-600/25">
            #{rank}
          </span>
          <span className="hidden rounded-xl bg-white/95 px-3 py-2 text-[11px] font-bold text-primary-700 shadow-sm backdrop-blur sm:inline-flex">
            Pilihan terbaik
          </span>
        </div>
      )}

      <span
        className={`absolute right-3 top-3 z-20 rounded-full px-3 py-1.5 text-[11px] font-extrabold tracking-wide text-white shadow-lg ${
          status.isOpen ? 'bg-emerald-500 shadow-emerald-500/25' : 'bg-red-500 shadow-red-500/25'
        }`}
      >
        {status.label}
      </span>

      <div className="relative aspect-[16/9] w-full overflow-hidden bg-slate-200">
        <img
          src={displayImage || fallbackImages[0]}
          alt={name || 'Restoran di Lombok'}
          className="h-full w-full object-cover transition duration-700 group-hover:scale-105"
          loading="lazy"
          onError={(event) => {
            event.currentTarget.src = fallbackImages[1];
          }}
        />
        <div className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-slate-950/75 via-slate-950/25 to-transparent" />

        <button
          className="absolute bottom-3 right-3 z-10 flex h-10 w-10 items-center justify-center rounded-xl bg-white/92 text-slate-500 shadow-sm backdrop-blur transition hover:scale-105 hover:text-accent-orange"
          onClick={(event) => event.stopPropagation()}
          aria-label="Simpan restoran"
        >
          <FiHeart className="h-4 w-4" />
        </button>
      </div>

      <div className="flex flex-1 flex-col p-5">
        <div className="mb-4 space-y-3">
          <div className="flex items-start justify-between gap-3">
            <h3 className="line-clamp-2 min-w-0 font-poppins text-xl font-extrabold leading-snug text-slate-950 transition group-hover:text-primary-700">
              {name || 'Restoran Lombok'}
            </h3>
          </div>

          <StarRating rating={rating} />

          {location && (
            <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
              <FiMapPin className="h-4 w-4 shrink-0 text-primary-500" />
              <span className="line-clamp-1">{location}</span>
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            {cuisineLabel && (
              <span className="max-w-full truncate rounded-full bg-orange-50 px-3 py-1.5 text-xs font-bold text-orange-700 ring-1 ring-orange-100">
                {cuisineLabel.length > 28 ? `${cuisineLabel.slice(0, 28)}...` : cuisineLabel}
              </span>
            )}
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700 ring-1 ring-emerald-100">
              <FaWallet className="h-3.5 w-3.5" aria-hidden="true" />
              {priceLabel}
            </span>
          </div>
        </div>

        {displayDescription && (
          <p className="mb-4 line-clamp-2 text-sm leading-6 text-slate-500">
            {String(displayDescription).length > 118
              ? `${String(displayDescription).slice(0, 118)}...`
              : String(displayDescription)}
          </p>
        )}

        {popular_dishes && popular_dishes.length > 0 && (
          <div className="mb-4 flex flex-wrap gap-1.5">
            {popular_dishes.slice(0, 3).map((dish, index) => (
              <span key={index} className="rounded-lg bg-slate-100 px-2.5 py-1 text-[11px] font-semibold text-slate-600">
                {dish}
              </span>
            ))}
          </div>
        )}

        <div className="mt-auto grid grid-cols-1 gap-2 border-t border-slate-100 pt-4 sm:grid-cols-2">
          <button
            className="min-h-[44px] rounded-xl bg-primary-600 px-4 text-sm font-bold text-white shadow-lg shadow-primary-600/20 transition hover:bg-primary-700 active:scale-[0.98]"
            onClick={(event) => {
              event.stopPropagation();
              onCardClick?.(restaurant);
            }}
          >
            Lihat Detail
          </button>
          <button
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 transition hover:border-primary-200 hover:bg-primary-50 hover:text-primary-700 active:scale-[0.98]"
            onClick={handleChatClick}
          >
            <FiMessageCircle className="h-4 w-4" aria-hidden="true" />
            Chat AI
          </button>
        </div>
      </div>
    </article>
  );
};

export default RestaurantCard;

const ChatRestaurantCard = ({ restaurant, onViewDetail }) => {
  const { name, rating, matchPercentage, cuisine, location, priceRange, isPreferred } = restaurant;

  const renderStars = (value) => {
    if (!value) return null;
    const number = Number(value);
    return (
      <div className="flex items-center gap-0.5">
        {[...Array(5)].map((_, index) => (
          <svg
            key={index}
            className={`h-3.5 w-3.5 ${index < Math.floor(number) ? 'text-amber-400' : 'text-slate-200'}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
        <span className="ml-1 text-xs font-semibold text-slate-500">{number.toFixed(1)}</span>
      </div>
    );
  };

  return (
    <div className="mb-2 max-w-[292px] rounded-2xl border border-slate-200 bg-white p-3.5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-slate-900/8">
      <div className="mb-2 flex items-start justify-between gap-2">
        <h4 className="line-clamp-2 text-sm font-bold leading-tight text-slate-950">{name}</h4>
        {isPreferred && (
          <span className="shrink-0 rounded-full bg-emerald-50 px-2 py-1 text-[10px] font-bold text-emerald-700 ring-1 ring-emerald-100">
            Match
          </span>
        )}
      </div>

      <div className="mb-3 flex items-center justify-between gap-2">
        {renderStars(rating)}
        {matchPercentage && (
          <span className="rounded-full bg-primary-50 px-2 py-1 text-[10px] font-extrabold text-primary-700">
            {matchPercentage}% cocok
          </span>
        )}
      </div>

      <div className="mb-3 flex flex-wrap gap-1.5">
        {location && <span className="rounded-lg bg-slate-100 px-2.5 py-1 text-[11px] font-semibold text-slate-600">{location}</span>}
        {cuisine && (
          <span className="rounded-lg bg-orange-50 px-2.5 py-1 text-[11px] font-semibold text-orange-700">
            {cuisine.length > 22 ? `${cuisine.slice(0, 22)}...` : cuisine}
          </span>
        )}
        {priceRange && <span className="rounded-lg bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold text-emerald-700">{priceRange}</span>}
      </div>

      <button
        onClick={() => onViewDetail?.(restaurant)}
        className="min-h-[36px] w-full rounded-xl bg-primary-50 text-center text-xs font-bold text-primary-700 transition hover:bg-primary-600 hover:text-white active:scale-[0.98]"
      >
        Lihat Detail
      </button>
    </div>
  );
};

export default ChatRestaurantCard;

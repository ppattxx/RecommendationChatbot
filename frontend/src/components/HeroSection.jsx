import { useEffect, useState } from 'react';
import { FiArrowDown, FiMapPin, FiMessageCircle, FiNavigation, FiSearch, FiStar } from 'react-icons/fi';

const heroImage =
  'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?auto=format&fit=crop&w=1600&q=85';

const chatMockMessages = [
  { type: 'user', text: 'Saya di Kuta, cari makan malam seafood yang santai.', delay: 0 },
  { type: 'bot', text: 'Cocok. Saya prioritaskan restoran dekat pantai, rating tinggi, dan suasana tidak terlalu formal.', delay: 850 },
  {
    type: 'recommendation',
    name: 'El Bazar Cafe & Restaurant',
    meta: 'Kuta Lombok - Mediterranean - 4.7',
    note: 'Pilihan nyaman setelah sunset, cocok untuk traveler yang ingin tempat rapi tanpa terasa kaku.',
    delay: 1650,
  },
];

const tripStats = [
  { value: '1.100+', label: 'pilihan restoran' },
  { value: '24/7', label: 'asisten perjalanan' },
  { value: 'Lombok', label: 'fokus destinasi' },
];

const headlineWords = ['Jelajahi', 'Kuliner', 'Terbaik', 'Lombok'];

const floatingTags = [
  { label: 'Seafood 🦐', className: 'left-4 top-28 sm:left-10 lg:left-[52%] lg:top-28', delay: '0s' },
  { label: 'Halal', className: 'right-5 top-44 sm:right-14 lg:right-12 lg:top-40', delay: '1.3s' },
  { label: 'Local Favorite', className: 'bottom-28 left-6 sm:left-16 lg:left-[56%] lg:bottom-24', delay: '2.1s' },
];

const HeroSection = ({ onOpenChat }) => {
  const [visibleMessages, setVisibleMessages] = useState(0);

  useEffect(() => {
    const timers = chatMockMessages.map((message, index) =>
      setTimeout(() => setVisibleMessages(index + 1), message.delay)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    onOpenChat?.();
  };

  return (
    <section id="hero" className="relative min-h-[94vh] overflow-hidden bg-primary-900 text-white">
      <div className="absolute inset-0 bg-[linear-gradient(135deg,#002FA7_0%,#064A9F_42%,#0AADAD_100%)]" />
      <img
        src={heroImage}
        alt="Destinasi Lombok"
        className="absolute inset-0 h-full w-full scale-110 object-cover opacity-30 blur-[3px] saturate-125"
      />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.18),transparent_28%),radial-gradient(circle_at_85%_20%,rgba(255,107,53,0.2),transparent_24%),linear-gradient(180deg,rgba(0,20,75,0.18),rgba(0,15,45,0.76))]" />
      <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-slate-950/70 to-transparent" />

      {floatingTags.map((tag) => (
        <div
          key={tag.label}
          className={`pointer-events-none absolute z-10 hidden rounded-full border border-white/20 bg-white/14 px-4 py-2 text-sm font-bold text-white shadow-2xl shadow-black/15 backdrop-blur-xl animate-float sm:block ${tag.className}`}
          style={{ animationDelay: tag.delay }}
        >
          {tag.label}
        </div>
      ))}

      <div className="relative z-20 mx-auto grid min-h-[94vh] w-full max-w-7xl items-center gap-10 px-4 pb-10 pt-28 sm:px-6 lg:grid-cols-[1.02fr_0.98fr] lg:px-8 lg:pt-24">
        <div className="max-w-3xl">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/12 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-white/88 backdrop-blur-md">
            <FiNavigation className="h-4 w-4" />
            Premium travel dining guide
          </div>

          <h1 className="font-poppins text-4xl font-extrabold leading-[1.02] text-white sm:text-5xl lg:text-7xl">
            {headlineWords.map((word, index) => (
              <span
                key={word}
                className="mr-3 inline-block animate-slide-up opacity-0 [animation-fill-mode:forwards] sm:mr-4"
                style={{ animationDelay: `${index * 150}ms` }}
              >
                {word}
              </span>
            ))}
          </h1>

          <p className="mt-5 max-w-2xl text-base leading-8 text-white/82 sm:text-lg">
            Dari warung lokal sampai dinner dekat pantai, Traveler membantu wisatawan menemukan tempat makan yang sesuai rute, mood, budget, dan selera kuliner di Lombok.
          </p>

          <form
            onSubmit={handleSearchSubmit}
            className="mt-7 flex w-full max-w-2xl flex-col gap-3 rounded-2xl border border-white/18 bg-white/14 p-2 shadow-2xl shadow-slate-950/18 backdrop-blur-xl sm:flex-row sm:items-center"
          >
            <label className="flex min-h-[56px] flex-1 items-center gap-3 rounded-xl bg-white px-4 text-slate-700 shadow-sm">
              <FiSearch className="h-5 w-5 shrink-0 text-primary-600" />
              <input
                type="text"
                placeholder="Mau makan apa? Di mana?"
                className="min-w-0 flex-1 bg-transparent text-sm font-semibold text-slate-900 outline-none placeholder:text-slate-400 sm:text-base"
                onFocus={onOpenChat}
              />
            </label>
            <button
              type="submit"
              className="inline-flex min-h-[56px] items-center justify-center gap-2 rounded-xl bg-accent-orange px-6 text-sm font-extrabold text-white shadow-xl shadow-orange-950/20 transition hover:-translate-y-0.5 hover:bg-orange-600 active:scale-[0.98]"
            >
              Search
              <FiArrowDown className="h-4 w-4 -rotate-90" />
            </button>
          </form>

          <div className="mt-5 flex flex-wrap gap-2 sm:hidden">
            {floatingTags.map((tag) => (
              <span key={tag.label} className="rounded-full border border-white/18 bg-white/12 px-3 py-1.5 text-xs font-bold text-white/88 backdrop-blur-md">
                {tag.label}
              </span>
            ))}
          </div>

          <div className="mt-8 grid max-w-xl grid-cols-3 divide-x divide-white/15 rounded-2xl border border-white/15 bg-white/10 backdrop-blur-md">
            {tripStats.map((stat) => (
              <div key={stat.label} className="px-3 py-4 text-center sm:px-5">
                <div className="font-poppins text-lg font-bold text-white sm:text-2xl">{stat.value}</div>
                <div className="mt-1 text-[11px] font-medium uppercase tracking-[0.12em] text-white/55 sm:text-xs">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-7 flex flex-col gap-3 sm:flex-row">
            <button
              onClick={onOpenChat}
              className="inline-flex min-h-[52px] items-center justify-center gap-3 rounded-xl bg-white px-6 py-3 text-sm font-bold text-primary-700 shadow-xl shadow-black/20 transition hover:-translate-y-0.5 hover:bg-slate-100"
            >
              <FiMessageCircle className="h-5 w-5" />
              Tanya Traveler
            </button>
            <a
              href="#top-picks"
              className="inline-flex min-h-[52px] items-center justify-center gap-3 rounded-xl border border-white/25 bg-white/10 px-6 py-3 text-sm font-bold text-white backdrop-blur-md transition hover:-translate-y-0.5 hover:bg-white/15"
            >
              Lihat tempat populer
              <FiArrowDown className="h-4 w-4" />
            </a>
          </div>
        </div>

        <div className="rounded-[1.75rem] border border-white/16 bg-white/12 p-3 shadow-2xl shadow-black/25 backdrop-blur-xl sm:p-4 lg:justify-self-end">
          <div className="overflow-hidden rounded-2xl bg-slate-50 text-slate-900 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-600 text-white">
                  <FiMapPin className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-bold">Traveler</p>
                  <p className="text-xs text-slate-500">Trip context aktif</p>
                </div>
              </div>
              <span className="rounded-full bg-teal-50 px-2.5 py-1 text-xs font-semibold text-teal-700">
                Online
              </span>
            </div>

            <div className="min-h-[280px] space-y-3 bg-slate-100/70 p-4 sm:p-5">
              {chatMockMessages.slice(0, visibleMessages).map((message, index) => {
                if (message.type === 'user') {
                  return (
                    <div key={index} className="flex justify-end animate-slide-up">
                      <div className="max-w-[82%] rounded-2xl rounded-br-sm bg-primary-600 px-4 py-3 text-sm leading-6 text-white">
                        {message.text}
                      </div>
                    </div>
                  );
                }

                if (message.type === 'recommendation') {
                  return (
                    <div key={index} className="flex justify-start animate-slide-up">
                      <div className="max-w-[92%] rounded-2xl rounded-bl-sm border border-slate-200 bg-white p-4 shadow-sm">
                        <div className="mb-2 flex items-start justify-between gap-3">
                          <div>
                            <p className="text-sm font-bold text-slate-950">{message.name}</p>
                            <p className="mt-1 text-xs text-slate-500">{message.meta}</p>
                          </div>
                          <FiStar className="mt-0.5 h-4 w-4 shrink-0 fill-amber-400 text-amber-400" />
                        </div>
                        <p className="text-sm leading-6 text-slate-600">{message.note}</p>
                      </div>
                    </div>
                  );
                }

                return (
                  <div key={index} className="flex justify-start animate-slide-up">
                    <div className="max-w-[86%] rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-700 shadow-sm">
                      {message.text}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex items-center gap-2 border-t border-slate-200 bg-white p-4">
              <div className="min-h-[42px] flex-1 rounded-xl bg-slate-100 px-4 py-3 text-sm text-slate-400">
                Tulis rencana makan Anda...
              </div>
              <button onClick={onOpenChat} className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent-orange text-white transition hover:bg-orange-600">
                <FiNavigation className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

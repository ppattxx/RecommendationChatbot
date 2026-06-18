import { useEffect, useState } from 'react';
import { FiChevronDown, FiMap, FiMenu, FiSearch, FiX } from 'react-icons/fi';
import { FaUtensils } from 'react-icons/fa';

const navLinks = [
  { label: 'Beranda', href: '#hero' },
  { label: 'Jelajah Restoran', href: '#top-picks' },
  { label: 'Tentang', href: '#footer' },
];

const destinations = ['Senggigi', 'Mataram', 'Gili Trawangan', 'Lombok Tengah'];

const Navbar = ({ onOpenChat }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [destinationOpen, setDestinationOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 18);
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileOpen]);

  const closeMenu = () => {
    setMobileOpen(false);
    setDestinationOpen(false);
  };

  const darkMode = scrolled || mobileOpen;

  return (
    <nav
      id="navbar"
      className={`fixed left-0 right-0 top-0 z-40 border-b transition-all duration-300 ${
        scrolled
          ? 'border-white/60 bg-white/78 py-3 shadow-lg shadow-slate-900/8 backdrop-blur-xl'
          : 'border-transparent bg-transparent py-5'
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <a href="#hero" onClick={closeMenu} className="group flex items-center gap-3">
          <span
            className={`relative flex h-11 w-11 items-center justify-center rounded-2xl transition-all duration-300 ${
              darkMode
                ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/25'
                : 'bg-white/16 text-white ring-1 ring-white/24 backdrop-blur-md'
            }`}
          >
            <FiMap className="h-5 w-5 transition-transform duration-300 group-hover:-rotate-12" aria-hidden="true" />
            <FaUtensils className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full bg-accent-orange p-1 text-white shadow-md" aria-hidden="true" />
          </span>
          <span
            className={`font-poppins text-xl font-extrabold leading-none tracking-normal transition-colors ${
              darkMode ? 'text-slate-950' : 'text-white'
            }`}
          >
            LombokEats
          </span>
        </a>

        <div className="hidden items-center gap-1 md:flex">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
                scrolled
                  ? 'text-slate-600 hover:bg-slate-100 hover:text-primary-700'
                  : 'text-white/82 hover:bg-white/12 hover:text-white'
              }`}
            >
              {link.label}
            </a>
          ))}

          <div className="relative" onMouseLeave={() => setDestinationOpen(false)}>
            <button
              type="button"
              onClick={() => setDestinationOpen((value) => !value)}
              onMouseEnter={() => setDestinationOpen(true)}
              className={`inline-flex items-center gap-1.5 rounded-xl px-4 py-2 text-sm font-semibold transition ${
                scrolled
                  ? 'text-slate-600 hover:bg-slate-100 hover:text-primary-700'
                  : 'text-white/82 hover:bg-white/12 hover:text-white'
              }`}
              aria-expanded={destinationOpen}
              aria-haspopup="menu"
            >
              Destinasi
              <FiChevronDown className={`h-4 w-4 transition-transform ${destinationOpen ? 'rotate-180' : ''}`} />
            </button>

            {destinationOpen && (
              <div className="absolute left-0 top-full mt-2 w-56 overflow-hidden rounded-2xl border border-white/70 bg-white/92 p-2 shadow-2xl shadow-slate-900/14 backdrop-blur-xl" role="menu">
                {destinations.map((destination) => (
                  <a
                    key={destination}
                    href="#top-picks"
                    className="flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-primary-50 hover:text-primary-700"
                    role="menuitem"
                  >
                    <FiMap className="h-4 w-4 text-primary-500" aria-hidden="true" />
                    {destination}
                  </a>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="hidden items-center gap-2 md:flex">
          <button
            onClick={onOpenChat}
            className="group relative inline-flex h-11 items-center gap-2 overflow-hidden rounded-xl bg-primary-600 px-5 text-sm font-bold text-white shadow-lg shadow-primary-600/22 transition hover:-translate-y-0.5 hover:bg-primary-700 hover:shadow-xl hover:shadow-primary-600/35"
          >
            <span className="absolute inset-y-0 -left-12 w-10 -skew-x-12 bg-white/35 opacity-0 transition-all duration-700 group-hover:left-[115%] group-hover:opacity-100" />
            <FiSearch className="h-4 w-4" aria-hidden="true" />
            <span className="relative">Cari Restoran</span>
          </button>
        </div>

        <button
          onClick={() => setMobileOpen((value) => !value)}
          className={`flex h-11 w-11 items-center justify-center rounded-xl transition md:hidden ${
            darkMode
              ? 'bg-slate-100 text-slate-900 hover:bg-slate-200'
              : 'bg-white/14 text-white ring-1 ring-white/20 hover:bg-white/22'
          }`}
          aria-label="Toggle navigation menu"
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? <FiX className="h-5 w-5" /> : <FiMenu className="h-5 w-5" />}
        </button>
      </div>

      <div
        className={`fixed inset-0 z-40 bg-slate-950/40 backdrop-blur-sm transition-opacity duration-300 md:hidden ${
          mobileOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={closeMenu}
        aria-hidden="true"
      />

      <aside
        className={`fixed right-0 top-0 z-50 flex h-dvh w-[min(86vw,360px)] flex-col border-l border-white/60 bg-white p-5 shadow-2xl shadow-slate-950/22 backdrop-blur-none transition-transform duration-300 md:hidden ${
          mobileOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        aria-hidden={!mobileOpen}
      >
        <div className="mb-6 flex items-center justify-between gap-4">
          <a href="#hero" onClick={closeMenu} className="flex min-w-0 items-center gap-3">
            <span className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-primary-600 text-white shadow-lg shadow-primary-600/25">
              <FiMap className="h-5 w-5" aria-hidden="true" />
              <FaUtensils className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full bg-accent-orange p-1 text-white shadow-md" aria-hidden="true" />
            </span>
            <span className="truncate font-poppins text-lg font-extrabold text-slate-950">LombokEats</span>
          </a>
          <button
            onClick={closeMenu}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-900 transition hover:bg-slate-200"
            aria-label="Close navigation menu"
          >
            <FiX className="h-5 w-5" />
          </button>
        </div>

        <div className="grid gap-1">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={closeMenu}
              className="rounded-xl px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 hover:text-primary-700"
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="mt-5 border-t border-slate-200 pt-5">
          <p className="mb-2 px-4 text-xs font-extrabold uppercase tracking-[0.16em] text-slate-400">Destinasi</p>
          <div className="grid gap-1">
            {destinations.map((destination) => (
              <a
                key={destination}
                href="#top-picks"
                onClick={closeMenu}
                className="flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-primary-50 hover:text-primary-700"
              >
                <FiMap className="h-4 w-4 text-primary-500" aria-hidden="true" />
                {destination}
              </a>
            ))}
          </div>
        </div>

        <button
          onClick={() => {
            closeMenu();
            onOpenChat?.();
          }}
          className="group relative mt-auto inline-flex min-h-[48px] items-center justify-center gap-2 overflow-hidden rounded-xl bg-primary-600 px-4 text-sm font-bold text-white shadow-lg shadow-primary-600/24 transition active:scale-[0.98]"
        >
          <span className="absolute inset-y-0 -left-12 w-10 -skew-x-12 bg-white/35 opacity-0 transition-all duration-700 group-hover:left-[115%] group-hover:opacity-100" />
          <FiSearch className="h-4 w-4" aria-hidden="true" />
          <span className="relative">Cari Restoran</span>
        </button>
      </aside>
    </nav>
  );
};

export default Navbar;

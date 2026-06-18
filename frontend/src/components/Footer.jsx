import { FiCompass, FiGithub, FiMapPin, FiMessageCircle, FiStar } from 'react-icons/fi';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer id="footer" className="bg-slate-950 text-white">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8 lg:py-16">
        <div className="grid gap-10 lg:grid-cols-[1.25fr_0.75fr_0.85fr]">
          <div>
            <div className="flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-white text-primary-700">
                <FiCompass className="h-5 w-5" />
              </span>
              <div>
                <p className="font-poppins text-xl font-extrabold">Traveler</p>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/45">LombokEats</p>
              </div>
            </div>
            <p className="mt-5 max-w-md text-sm leading-7 text-white/58">
              Asisten rekomendasi restoran untuk wisatawan Lombok. Cari tempat makan berdasarkan area, suasana, budget, dan selera tanpa harus membuka banyak tab.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              {['Primary blue', 'Accent orange', 'Poppins UI'].map((item) => (
                <span key={item} className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white/58">
                  {item}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h4 className="mb-4 font-poppins text-sm font-bold text-white">Fitur Utama</h4>
            <ul className="space-y-3 text-sm text-white/55">
              <li className="flex items-center gap-3"><FiMessageCircle className="h-4 w-4 text-accent-orange" /> Chat rekomendasi</li>
              <li className="flex items-center gap-3"><FiMapPin className="h-4 w-4 text-accent-orange" /> Filter area Lombok</li>
              <li className="flex items-center gap-3"><FiStar className="h-4 w-4 text-accent-orange" /> Ranking personal</li>
            </ul>
          </div>

          <div>
            <h4 className="mb-4 font-poppins text-sm font-bold text-white">Tentang Proyek</h4>
            <p className="text-sm leading-7 text-white/55">
              Dibangun dengan React, Vite, TailwindCSS, dan backend rekomendasi restoran berbasis content-based filtering untuk kebutuhan Tugas Akhir.
            </p>
            <a
              href="#"
              className="mt-5 inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-white/60 transition hover:bg-white/10 hover:text-white"
              aria-label="GitHub"
            >
              <FiGithub className="h-4 w-4" />
            </a>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-white/10 pt-6 text-xs text-white/38 sm:flex-row sm:items-center sm:justify-between">
          <p>Copyright {currentYear} Traveler by LombokEats.</p>
          <p>Primary #002FA7 - Accent #FF6B35</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

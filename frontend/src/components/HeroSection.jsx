/**
 * HeroSection Component
 * Full-width hero with persuasive headline and animated chat mockup.
 */
import { useState, useEffect } from 'react';

const chatMockMessages = [
  { type: 'user', text: 'Cari seafood enak di Senggigi', delay: 0 },
  {
    type: 'bot',
    text: 'Saya menemukan 3 restoran terbaik untuk Anda! 🎯',
    delay: 800,
  },
  {
    type: 'bot-card',
    name: 'De Quake Restaurant',
    rating: 4.7,
    cuisine: 'Seafood',
    location: 'Senggigi',
    delay: 1500,
  },
];

const HeroSection = ({ onOpenChat }) => {
  const [visibleMessages, setVisibleMessages] = useState(0);

  useEffect(() => {
    const timers = chatMockMessages.map((msg, index) =>
      setTimeout(() => setVisibleMessages(index + 1), msg.delay + 600)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  const stats = [
    { icon: '📍', value: '500+', label: 'Restoran' },
    { icon: '🗺️', value: '50+', label: 'Lokasi' },
    { icon: '🤖', value: 'AI', label: 'Powered' },
  ];

  return (
    <section
      id="hero"
      className="relative min-h-[92vh] flex items-center overflow-hidden pt-20"
    >
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-white via-primary-50/40 to-primary-100/30" />
      {/* Decorative blobs */}
      <div className="absolute -top-32 -right-32 w-[500px] h-[500px] bg-primary-100/40 rounded-full blur-3xl animate-float" />
      <div className="absolute -bottom-40 -left-40 w-[600px] h-[600px] bg-accent-teal/10 rounded-full blur-3xl animate-float-delayed" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left — Copy */}
          <div className="space-y-8 animate-fade-in">
            <h1 className="text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold font-poppins text-gray-900 leading-tight">
              Temukan Rasa Sejati{' '}
              <span className="gradient-text">Lombok</span>{' '}
              dengan Kecerdasan{' '}
              <span className="relative inline-block">
                <span className="gradient-text">AI</span>
                <svg className="absolute -bottom-1 left-0 w-full" viewBox="0 0 100 8" preserveAspectRatio="none">
                  <path d="M0 7 Q 25 0, 50 4 Q 75 8, 100 1" stroke="#FF6B35" strokeWidth="2.5" fill="none" strokeLinecap="round" />
                </svg>
              </span>
            </h1>

            <p className="text-lg text-gray-500 max-w-lg leading-relaxed">
              Cukup ceritakan selera Anda dari lokasi, jenis masakan, suasana, hingga budget 
              dan AI kami akan merekomendasikan restoran terbaik di Lombok secara instan.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={onOpenChat}
                className="btn-primary text-base py-4 px-8 flex items-center justify-center gap-3 group"
              >
                <svg className="w-5 h-5 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Mulai Jelajahi
              </button>
              <a
                href="#top-picks"
                className="btn-secondary text-base py-4 px-8 flex items-center justify-center gap-2"
              >
                Lihat Restoran
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </a>
            </div>

            {/* Stats */}
            <div className="flex gap-8 pt-4">
              {stats.map((stat) => (
                <div key={stat.label} className="text-center">
                  <div className="text-2xl mb-1">{stat.icon}</div>
                  <div className="text-xl font-bold text-gray-900 font-poppins">{stat.value}</div>
                  <div className="text-xs text-gray-400 font-medium">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Right — Chat Mockup */}
          <div className="hidden lg:flex justify-center animate-slide-in-right">
            <div className="w-[380px] bg-white rounded-3xl shadow-2xl shadow-primary-600/10 border border-gray-100 overflow-hidden">
              {/* Mock Header */}
              <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-5 flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <span className="text-white text-lg">🤖</span>
                </div>
                <div>
                  <p className="text-white font-semibold text-sm">LombokEats AI</p>
                  <p className="text-primary-200 text-xs flex items-center gap-1">
                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                    Online
                  </p>
                </div>
              </div>

              {/* Mock Messages */}
              <div className="p-5 space-y-4 min-h-[320px] bg-gradient-to-b from-gray-50/50 to-white">
                {chatMockMessages.slice(0, visibleMessages).map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}
                  >
                    {msg.type === 'user' && (
                      <div className="bg-gradient-to-br from-primary-600 to-primary-700 text-white px-4 py-2.5 rounded-2xl rounded-br-sm max-w-[80%] text-sm shadow-sm">
                        {msg.text}
                      </div>
                    )}
                    {msg.type === 'bot' && (
                      <div className="flex gap-2 items-end max-w-[85%]">
                        <div className="w-7 h-7 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
                          <span className="text-xs font-bold text-primary-700">AI</span>
                        </div>
                        <div className="bg-white border border-gray-100 px-4 py-2.5 rounded-2xl rounded-bl-sm text-sm text-gray-700 shadow-sm">
                          {msg.text}
                        </div>
                      </div>
                    )}
                    {msg.type === 'bot-card' && (
                      <div className="flex gap-2 items-end max-w-[92%]">
                        <div className="w-7 h-7 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
                          <span className="text-xs font-bold text-primary-700">AI</span>
                        </div>
                        <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-sm p-3.5 shadow-sm w-full">
                          <p className="font-semibold text-sm text-gray-900 mb-1.5">{msg.name}</p>
                          <div className="flex items-center gap-1 mb-2">
                            {[...Array(5)].map((_, i) => (
                              <svg key={i} className={`w-3.5 h-3.5 ${i < Math.floor(msg.rating) ? 'text-yellow-400' : 'text-gray-200'}`} fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                              </svg>
                            ))}
                            <span className="text-xs text-gray-500 ml-1">{msg.rating}</span>
                          </div>
                          <div className="flex gap-2">
                            <span className="badge-pill bg-primary-50 text-primary-700 text-[10px]">📍 {msg.location}</span>
                            <span className="badge-pill bg-accent-orange/10 text-accent-orange text-[10px]">🍽️ {msg.cuisine}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Mock Input */}
              <div className="p-4 border-t border-gray-100 flex gap-2">
                <div className="flex-1 bg-gray-50 rounded-full px-4 py-2.5 text-sm text-gray-400">
                  Ketik pesan Anda...
                </div>
                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

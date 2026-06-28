import { useCallback, useEffect, useRef, useState } from 'react';
import { FiMessageCircle, FiRefreshCw, FiSend, FiX } from 'react-icons/fi';
import { chatAPI } from '../services/api';
import { usePersonalization } from '../contexts/PersonalizationContext';
import { parseRecommendations } from '../utils/chatParser';
import ChatRestaurantCard from './ChatRestaurantCard';

const CHAT_STORAGE_KEY = 'chat_history';

const DEFAULT_WELCOME_MESSAGE =
  "Halo, saya Traveler. Ceritakan rencana makan Anda di Lombok, misalnya area, budget, suasana, dan jenis makanan yang diinginkan.\n\n" +
  "Contoh pertanyaan:\n" +
  "- Seafood santai di Senggigi\n" +
  "- Restoran romantis untuk dinner\n" +
  "- Tempat makan keluarga yang murah";

const TypingIndicator = () => (
  <div className="flex items-end justify-start gap-2">
    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-600 text-white shadow-sm">
      <span className="text-xs font-bold">AI</span>
    </div>
    <div className="rounded-2xl rounded-tl-none border border-slate-200 bg-slate-50 px-5 py-3.5 shadow-sm">
      <div className="flex items-end gap-1.5" aria-label="AI sedang mengetik">
        {[0, 1, 2].map((item) => (
          <span
            key={item}
            className="h-2 w-2 rounded-full bg-primary-500"
            style={{ animation: 'typingDot 1.1s ease-in-out infinite', animationDelay: `${item * 0.16}s` }}
          />
        ))}
      </div>
    </div>
  </div>
);

const MessageBubble = ({ message, formatTime, onViewDetail }) => {
  const isUser = message.type === 'user';
  const parsed = !isUser ? parseRecommendations(message.text) : null;

  if (isUser) {
    return (
      <div className="flex animate-slide-up items-end justify-end gap-2">
        <div className="max-w-[82%]">
          <div className="rounded-2xl rounded-tr-none bg-primary-800 px-4 py-3 text-white shadow-md shadow-primary-900/15">
            <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">{message.text}</p>
          </div>
          <p className="mt-1 pr-1 text-right text-[10px] text-slate-400">{formatTime(message.timestamp)}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex animate-slide-up items-end justify-start gap-2">
      <div className="mb-6 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-600 text-white shadow-sm">
        <span className="text-xs font-bold">AI</span>
      </div>
      <div className="max-w-[86%]">
        {parsed ? (
          <div className="space-y-2">
            {parsed.intro && (
              <div className="rounded-2xl rounded-tl-none border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm">
                <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">{parsed.intro}</p>
              </div>
            )}

            <div className="space-y-2 pl-1">
              {parsed.restaurants.map((restaurant, index) => (
                <div key={index} className="animate-slide-up" style={{ animationDelay: `${index * 90}ms`, animationFillMode: 'backwards' }}>
                  <ChatRestaurantCard restaurant={restaurant} onViewDetail={() => onViewDetail && onViewDetail(restaurant)} />
                </div>
              ))}
            </div>

            {parsed.followUp && (
              <div className="rounded-2xl rounded-tl-none border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm">
                <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-600">{parsed.followUp}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="rounded-2xl rounded-tl-none border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm">
            <p className="whitespace-pre-wrap break-words text-sm leading-relaxed text-slate-700">{message.text}</p>
          </div>
        )}
        <p className="mt-1 pl-1 text-[10px] text-slate-400">{formatTime(message.timestamp)}</p>
      </div>
    </div>
  );
};

const FloatingChatbot = ({ forceOpen, onClose, onViewDetail }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const {
    sessionId,
    deviceToken,
    updateSession,
    refreshPersonalization,
    resetAllData,
    updateLatestUserQuery,
  } = usePersonalization();

  useEffect(() => {
    if (forceOpen) setIsOpen(true);
  }, [forceOpen]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    if (messages.length > 0) {
      try {
        sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
      } catch (error) {
        console.error('Error saving chat to sessionStorage:', error);
      }
    }
  }, [messages]);

  const initializeNewChat = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await chatAPI.sendMessage('halo', null, deviceToken);
      if (response.success) {
        if (response.data.session_id) updateSession(response.data.session_id);
        setMessages([
          {
            type: 'bot',
            text: response.data.bot_response,
            timestamp: new Date(response.data.timestamp),
            synced: true,
          },
        ]);
      } else {
        setMessages([{ type: 'bot', text: DEFAULT_WELCOME_MESSAGE, timestamp: new Date(), synced: false }]);
      }
    } catch {
      setMessages([{ type: 'bot', text: DEFAULT_WELCOME_MESSAGE, timestamp: new Date(), synced: false }]);
    } finally {
      setIsLoading(false);
    }
  }, [deviceToken, updateSession]);

  const loadChatHistory = useCallback(async () => {
    setIsLoadingHistory(true);
    try {
      const localHistory = sessionStorage.getItem(CHAT_STORAGE_KEY);
      if (localHistory) {
        const parsedHistory = JSON.parse(localHistory);
        if (Array.isArray(parsedHistory) && parsedHistory.length > 0) {
          setMessages(parsedHistory.map((message) => ({ ...message, timestamp: new Date(message.timestamp) })));
          setHistoryLoaded(true);
          setIsLoadingHistory(false);
          return;
        }
      }

      if (sessionId) {
        const response = await chatAPI.getChatHistory(sessionId);
        if (response.success && response.data?.messages?.length > 0) {
          const backendMessages = [];
          response.data.messages.forEach((message) => {
            if (message.user_message) {
              backendMessages.push({ type: 'user', text: message.user_message, timestamp: new Date(message.timestamp), synced: true });
            }
            if (message.bot_response) {
              backendMessages.push({ type: 'bot', text: message.bot_response, timestamp: new Date(message.timestamp), synced: true });
            }
          });

          if (backendMessages.length > 0) {
            setMessages(backendMessages);
            sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(backendMessages));
            setHistoryLoaded(true);
            setIsLoadingHistory(false);
            return;
          }
        }
      }

      initializeNewChat();
    } catch (error) {
      console.error('Error loading chat history:', error);
      initializeNewChat();
    } finally {
      setIsLoadingHistory(false);
      setHistoryLoaded(true);
    }
  }, [initializeNewChat, sessionId]);

  useEffect(() => {
    if (isOpen && !historyLoaded) loadChatHistory();
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 300);
  }, [historyLoaded, isOpen, loadChatHistory]);

  const handleSendMessage = async (event) => {
    event.preventDefault();
    if (!inputMessage.trim()) return;

    const outgoingText = inputMessage.trim();
    updateLatestUserQuery(outgoingText);

    const userMessage = { type: 'user', text: outgoingText, timestamp: new Date(), synced: false };
    setMessages((current) => [...current, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(outgoingText, sessionId, deviceToken);
      if (response.success) {
        if (response.data.session_id && response.data.session_id !== sessionId) updateSession(response.data.session_id);
        const botMessage = {
          type: 'bot',
          text: response.data.bot_response,
          timestamp: new Date(response.data.timestamp),
          synced: true,
        };
        setMessages((current) => [...current.map((message) => (message === userMessage ? { ...message, synced: true } : message)), botMessage]);
        await refreshPersonalization();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((current) => [
        ...current,
        { type: 'bot', text: 'Maaf, terjadi kesalahan. Silakan coba lagi.', timestamp: new Date(), synced: false },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetHistory = async () => {
<<<<<<< Updated upstream
    if (!confirm('Reset semua riwayat chat dan preferensi? Aksi ini membuat session baru dan mengganti device token.')) return;
=======
    if (
      confirm(
        'Yakin ingin mereset SEMUA riwayat chat dan preferensi?\n\nAksi ini juga akan membuat session baru dan mengganti device token.'
      )
    ) {
      try {
        const result = await resetAllData();
        if (result?.success) {
          setMessages([]);
          setHistoryLoaded(false);
          sessionStorage.removeItem(CHAT_STORAGE_KEY);
>>>>>>> Stashed changes

    try {
      const result = await resetAllData();
      if (result?.success) {
        setMessages([]);
        setHistoryLoaded(false);
        localStorage.removeItem(CHAT_STORAGE_KEY);

        const init = await chatAPI.sendMessage('halo', null, result.newToken);
        if (init?.success) {
          if (init.data?.session_id) updateSession(init.data.session_id);
          setMessages([
            {
              type: 'bot',
              text: init.data?.bot_response || DEFAULT_WELCOME_MESSAGE,
              timestamp: new Date(init.data?.timestamp || Date.now()),
              synced: true,
            },
          ]);
        } else {
          setMessages([{ type: 'bot', text: DEFAULT_WELCOME_MESSAGE, timestamp: new Date(), synced: false }]);
        }

        await refreshPersonalization();
        alert('Riwayat berhasil direset. Session baru sudah dibuat.');
      } else {
        alert('Gagal mereset data. Silakan coba lagi.');
      }
    } catch (error) {
      console.error('Error resetting history:', error);
      alert('Gagal mereset data. Silakan coba lagi.');
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    onClose?.();
  };

  const formatTime = (date) => {
    const value = date instanceof Date ? date : new Date(date);
    return new Intl.DateTimeFormat('id-ID', { hour: '2-digit', minute: '2-digit' }).format(value);
  };

  const quickSuggestions = [
    'Seafood dekat Senggigi',
    'Restoran romantis',
    'Makan hemat di Kuta',
    'Cafe santai sore hari',
  ];

  return (
    <div className="fixed bottom-4 right-4 z-50 sm:bottom-6 sm:right-6">
      {isOpen && (
        <div className="mb-4 flex flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl shadow-slate-950/25 animate-slide-up
          w-[calc(100vw-2rem)] h-[min(75vh,560px)]
          sm:w-[380px] sm:h-[560px]
          md:w-[420px] md:h-[650px]">
          <div className="flex shrink-0 items-center justify-between bg-gradient-to-r from-primary-700 via-primary-600 to-sky-500 px-5 py-4 text-white">
            <div className="flex items-center gap-3">
              <div className="relative flex h-10 w-10 items-center justify-center rounded-2xl bg-white/18 backdrop-blur-sm">
                <span className="absolute -right-0.5 -top-0.5 h-3 w-3 rounded-full bg-emerald-300 ring-2 ring-white" />
                <span className="absolute -right-0.5 -top-0.5 h-3 w-3 animate-ping rounded-full bg-emerald-300/80" />
                <span className="text-xs font-bold">AI</span>
              </div>
              <div>
                <h3 className="font-poppins text-base font-bold">Traveler</h3>
                <p className="flex items-center gap-1.5 text-xs text-white/72">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                  Online - siap membantu
                </p>
              </div>
            </div>
            <div className="flex gap-1.5">
              <button onClick={handleResetHistory} className="rounded-lg p-2 transition hover:bg-white/15" title="Reset history">
                <FiRefreshCw size={16} />
              </button>
              <button onClick={handleClose} className="rounded-lg p-2 transition hover:bg-white/15" aria-label="Tutup chat">
                <FiX size={20} />
              </button>
            </div>
          </div>

          <div className="chat-scroll flex-1 space-y-4 overflow-y-auto bg-gradient-to-b from-slate-100 to-white p-4 sm:p-5">
            {isLoadingHistory && (
              <div className="space-y-4 animate-pulse">
                {[1, 2, 3].map((item) => (
                  <div key={item} className={`flex items-end gap-2 ${item % 2 === 0 ? 'justify-end' : 'justify-start'}`}>
                    {item % 2 !== 0 && <div className="h-8 w-8 rounded-full bg-slate-200" />}
                    <div className={`max-w-[75%] rounded-2xl p-3.5 ${item % 2 === 0 ? 'bg-slate-200' : 'bg-slate-100'}`}>
                      <div className="mb-2 h-4 w-32 rounded bg-slate-200" />
                      <div className="h-3 w-20 rounded bg-slate-200" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!isLoadingHistory && messages.length === 0 && !isLoading && (
              <div className="mt-12 text-center text-slate-400">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-50">
                  <FiMessageCircle size={28} className="text-primary-500" />
                </div>
                <p className="text-sm font-semibold text-slate-500">Belum ada percakapan</p>
                <p className="mt-1 text-xs text-slate-400">Mulai chat untuk rekomendasi perjalanan makan</p>
              </div>
            )}

            {messages.map((message, index) => (
              <MessageBubble key={index} message={message} formatTime={formatTime} onViewDetail={onViewDetail} />
            ))}

            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          {messages.length <= 1 && !isLoading && !isLoadingHistory && (
            <div className="shrink-0 px-4 pb-2 sm:px-5">
              <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">Coba tanyakan:</p>
              <div className="flex flex-wrap gap-1.5">
                {quickSuggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInputMessage(suggestion)}
                    className="rounded-full border border-primary-100 bg-primary-50 px-3 py-1.5 text-xs font-semibold text-primary-700 transition hover:bg-primary-100 active:scale-[0.98]"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          <form onSubmit={handleSendMessage} className="sticky bottom-0 z-10 shrink-0 border-t border-slate-100 bg-white/96 p-3 shadow-[0_-18px_36px_rgba(15,23,42,0.08)] backdrop-blur sm:p-4">
            <div className="flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(event) => setInputMessage(event.target.value)}
                placeholder="Ceritakan rencana makan Anda..."
                className="min-w-0 flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-primary-300 focus:ring-2 focus:ring-primary-400/40"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="rounded-xl bg-accent-orange p-3 text-white shadow-lg shadow-orange-500/25 transition hover:bg-orange-600 active:scale-95 disabled:bg-slate-300 disabled:shadow-none"
                aria-label="Kirim pesan"
              >
                <FiSend size={18} />
              </button>
            </div>
          </form>
        </div>
      )}

      <button
        onClick={() => {
          if (isOpen) handleClose();
          else setIsOpen(true);
        }}
        className={`group flex min-h-[56px] items-center justify-center gap-2 overflow-hidden rounded-full bg-primary-600 px-5 py-4 text-white shadow-2xl shadow-primary-600/30 transition hover:scale-105 hover:bg-primary-700 active:scale-95 ${!isOpen ? 'animate-pulse-glow' : ''}`}
        aria-label="Toggle chatbot"
      >
        {isOpen ? <FiX size={22} /> : <FiMessageCircle size={22} />}
        <span className="max-w-0 whitespace-nowrap text-sm font-extrabold opacity-0 transition-all duration-300 group-hover:max-w-[110px] group-hover:opacity-100">
          {isOpen ? 'Tutup' : `Chat AI ${String.fromCodePoint(0x1f916)}`}
        </span>
      </button>
    </div>
  );
};

export default FloatingChatbot;

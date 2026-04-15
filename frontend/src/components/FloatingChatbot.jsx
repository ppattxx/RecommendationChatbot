/**
 * Floating Chatbot Widget Component — LombokEats Redesign
 * Features:
 * - PENS Blue (#002FA7) design system
 * - Multi-turn conversation with message history
 * - Inline recommendation cards parsed from bot text
 * - Typing indicator with animated dots
 * - Mobile-responsive (full-width on small screens)
 * - Quick suggestion chips
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { FiMessageCircle, FiX, FiSend, FiRefreshCw } from 'react-icons/fi';
import { chatAPI } from '../services/api';
import { usePersonalization } from '../contexts/PersonalizationContext';
import { parseRecommendations } from '../utils/chatParser';
import ChatRestaurantCard from './ChatRestaurantCard';

const CHAT_STORAGE_KEY = 'chat_history';

const DEFAULT_WELCOME_MESSAGE =
  "Halo! 👋 Saya LombokEats AI, siap membantu Anda mencari restoran di Lombok!\n\n" +
  "Ceritakan apa yang Anda cari, misalnya:\n" +
  "• Seafood enak di Senggigi\n" +
  "• Restoran romantis untuk dinner\n" +
  "• Tempat makan keluarga yang murah";

/**
 * Typing indicator with staggered bouncing dots
 */
const TypingIndicator = () => (
  <div className="flex items-end gap-2 justify-start">
    <div className="w-8 h-8 rounded-full bg-primary-50 flex items-center justify-center shrink-0">
      <span className="text-primary-700 text-xs font-bold">AI</span>
    </div>
    <div className="bg-white rounded-2xl rounded-bl-sm px-5 py-3.5 shadow-sm border border-gray-100">
      <div className="flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 bg-primary-400 rounded-full"
            style={{
              animation: 'typingDot 1.4s ease-in-out infinite',
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>
    </div>
  </div>
);

/**
 * Message bubble component — renders normal text or recommendation cards
 */
const MessageBubble = ({ message, formatTime, onViewDetail }) => {
  const isUser = message.type === 'user';

  // Try to parse bot messages for recommendations
  const parsed = !isUser ? parseRecommendations(message.text) : null;

  if (isUser) {
    return (
      <div className="flex items-end gap-2 justify-end animate-slide-up">
        <div className="max-w-[80%]">
          <div className="bg-gradient-to-br from-primary-600 to-primary-700 text-white px-4 py-3 rounded-2xl rounded-br-sm shadow-sm">
            <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
              {message.text}
            </p>
          </div>
          <p className="text-[10px] text-gray-400 mt-1 text-right pr-1">
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    );
  }

  // Bot message — with or without recommendation cards
  return (
    <div className="flex items-end gap-2 justify-start animate-slide-up">
      <div className="w-8 h-8 rounded-full bg-primary-50 flex items-center justify-center shrink-0 mb-6">
        <span className="text-primary-700 text-xs font-bold">AI</span>
      </div>
      <div className="max-w-[85%]">
        {parsed ? (
          /* Structured recommendation response */
          <div className="space-y-2">
            {/* Intro text */}
            {parsed.intro && (
              <div className="bg-white border border-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm">
                <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {parsed.intro}
                </p>
              </div>
            )}

            {/* Restaurant cards */}
            <div className="space-y-2 pl-1">
              {parsed.restaurants.map((resto, idx) => (
                <div
                  key={idx}
                  className="animate-slide-up"
                  style={{ animationDelay: `${idx * 100}ms`, animationFillMode: 'backwards' }}
                >
                  <ChatRestaurantCard
                    restaurant={resto}
                    onViewDetail={() => onViewDetail && onViewDetail(resto)}
                  />
                </div>
              ))}
            </div>

            {/* Follow-up */}
            {parsed.followUp && (
              <div className="bg-white border border-gray-100 px-4 py-3 rounded-2xl shadow-sm">
                <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">
                  {parsed.followUp}
                </p>
              </div>
            )}
          </div>
        ) : (
          /* Regular text message */
          <div className="bg-white border border-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm">
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap break-words">
              {message.text}
            </p>
          </div>
        )}
        <p className="text-[10px] text-gray-400 mt-1 pl-1">
          {formatTime(message.timestamp)}
        </p>
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

  // Sync forceOpen prop
  useEffect(() => {
    if (forceOpen) {
      setIsOpen(true);
    }
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
        localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
      } catch (error) {
        console.error('Error saving chat to localStorage:', error);
      }
    }
  }, [messages]);

  useEffect(() => {
    if (isOpen && !historyLoaded) {
      loadChatHistory();
    }
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen, historyLoaded]);

  const loadChatHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const localHistory = localStorage.getItem(CHAT_STORAGE_KEY);
      if (localHistory) {
        const parsedHistory = JSON.parse(localHistory);
        if (Array.isArray(parsedHistory) && parsedHistory.length > 0) {
          const formattedHistory = parsedHistory.map((msg) => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
          }));
          setMessages(formattedHistory);
          setHistoryLoaded(true);
          setIsLoadingHistory(false);
          return;
        }
      }

      if (sessionId) {
        const response = await chatAPI.getChatHistory(sessionId);
        if (response.success && response.data?.messages?.length > 0) {
          const backendMessages = [];
          response.data.messages.forEach((msg) => {
            if (msg.user_message) {
              backendMessages.push({
                type: 'user',
                text: msg.user_message,
                timestamp: new Date(msg.timestamp),
                synced: true,
              });
            }
            if (msg.bot_response) {
              backendMessages.push({
                type: 'bot',
                text: msg.bot_response,
                timestamp: new Date(msg.timestamp),
                synced: true,
              });
            }
          });

          if (backendMessages.length > 0) {
            setMessages(backendMessages);
            localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(backendMessages));
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
  };

  const initializeNewChat = async () => {
    setIsLoading(true);
    try {
      const response = await chatAPI.sendMessage('halo', null, deviceToken);
      if (response.success) {
        if (response.data.session_id) {
          updateSession(response.data.session_id);
        }
        setMessages([{
          type: 'bot',
          text: response.data.bot_response,
          timestamp: new Date(response.data.timestamp),
          synced: true,
        }]);
      } else {
        setMessages([{
          type: 'bot',
          text: DEFAULT_WELCOME_MESSAGE,
          timestamp: new Date(),
          synced: false,
        }]);
      }
    } catch {
      setMessages([{
        type: 'bot',
        text: DEFAULT_WELCOME_MESSAGE,
        timestamp: new Date(),
        synced: false,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const outgoingText = inputMessage.trim();
    updateLatestUserQuery(outgoingText);

    const userMessage = {
      type: 'user',
      text: outgoingText,
      timestamp: new Date(),
      synced: false,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(outgoingText, sessionId, deviceToken);
      if (response.success) {
        if (response.data.session_id && response.data.session_id !== sessionId) {
          updateSession(response.data.session_id);
        }

        const botMessage = {
          type: 'bot',
          text: response.data.bot_response,
          timestamp: new Date(response.data.timestamp),
          synced: true,
        };

        setMessages((prev) => {
          const updated = prev.map((msg) =>
            msg === userMessage ? { ...msg, synced: true } : msg
          );
          return [...updated, botMessage];
        });

        await refreshPersonalization();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          type: 'bot',
          text: 'Maaf, terjadi kesalahan. Silakan coba lagi.',
          timestamp: new Date(),
          synced: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetHistory = async () => {
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
          localStorage.removeItem(CHAT_STORAGE_KEY);

          // Start a brand-new conversation using the NEW token (no page reload).
          const init = await chatAPI.sendMessage('halo', null, result.newToken);
          if (init?.success) {
            if (init.data?.session_id) {
              updateSession(init.data.session_id);
            }
            setMessages([
              {
                type: 'bot',
                text: init.data?.bot_response || DEFAULT_WELCOME_MESSAGE,
                timestamp: new Date(init.data?.timestamp || Date.now()),
                synced: true,
              },
            ]);
          } else {
            setMessages([
              {
                type: 'bot',
                text: DEFAULT_WELCOME_MESSAGE,
                timestamp: new Date(),
                synced: false,
              },
            ]);
          }

          await refreshPersonalization();
          alert('Berhasil reset total: history dihapus, session baru dibuat, dan device token diganti.');
        } else {
          alert('Gagal mereset data. Silakan coba lagi.');
        }
      } catch (error) {
        console.error('Error resetting history:', error);
        alert('Gagal mereset data. Silakan coba lagi.');
      }
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    onClose?.();
  };

  const formatTime = (date) => {
    if (!(date instanceof Date)) date = new Date(date);
    return new Intl.DateTimeFormat('id-ID', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const quickSuggestions = [
    'Seafood di Senggigi',
    'Restoran romantis',
    'Makanan murah di Kuta',
    'Cafe santai',
  ];

  return (
    <div className="fixed bottom-5 right-5 z-50 sm:bottom-6 sm:right-6">
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-[calc(100vw-2.5rem)] sm:w-[420px] h-[calc(100vh-6rem)] sm:h-[650px] bg-white rounded-2xl sm:rounded-3xl shadow-2xl shadow-gray-900/15 flex flex-col animate-slide-up border border-gray-200/60 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 via-primary-600 to-primary-700 text-white px-5 py-4 flex justify-between items-center shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/15 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <span className="text-lg">🌴</span>
              </div>
              <div>
                <h3 className="font-bold text-base font-poppins">LombokEats AI</h3>
                <p className="text-xs text-primary-200 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                  Online • Siap membantu
                </p>
              </div>
            </div>
            <div className="flex gap-1.5">
              <button
                onClick={handleResetHistory}
                className="hover:bg-white/15 p-2 rounded-lg transition-colors"
                title="Reset History + Session + Device Token"
              >
                <FiRefreshCw size={16} />
              </button>
              <button
                onClick={handleClose}
                className="hover:bg-white/15 p-2 rounded-lg transition-colors"
              >
                <FiX size={20} />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 bg-gradient-to-b from-gray-50/80 to-white chat-scroll">
            {/* Loading History Skeleton */}
            {isLoadingHistory && (
              <div className="space-y-4 animate-pulse">
                {[1, 2, 3].map((i) => (
                  <div key={i} className={`flex items-end gap-2 ${i % 2 === 0 ? 'justify-end' : 'justify-start'}`}>
                    {i % 2 !== 0 && <div className="w-8 h-8 bg-gray-200 rounded-full" />}
                    <div className={`max-w-[75%] rounded-2xl p-3.5 ${i % 2 === 0 ? 'bg-gray-200' : 'bg-gray-100'}`}>
                      <div className="h-4 bg-gray-200 rounded w-32 mb-2" />
                      <div className="h-3 bg-gray-200 rounded w-20" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Empty State */}
            {!isLoadingHistory && messages.length === 0 && !isLoading && (
              <div className="text-center text-gray-400 mt-12">
                <div className="w-16 h-16 bg-primary-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <FiMessageCircle size={28} className="text-primary-400" />
                </div>
                <p className="text-sm font-medium">Belum ada percakapan</p>
                <p className="text-xs mt-1 text-gray-300">Mulai chat untuk rekomendasi restoran</p>
              </div>
            )}

            {/* Messages */}
            {messages.map((message, index) => (
              <MessageBubble
                key={index}
                message={message}
                formatTime={formatTime}
                onViewDetail={onViewDetail}
              />
            ))}

            {/* Typing Indicator */}
            {isLoading && <TypingIndicator />}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestions */}
          {messages.length <= 1 && !isLoading && !isLoadingHistory && (
            <div className="px-4 sm:px-5 pb-2 shrink-0">
              <p className="text-[10px] text-gray-400 mb-2 font-medium uppercase tracking-wider">
                💡 Coba tanyakan:
              </p>
              <div className="flex flex-wrap gap-1.5">
                {quickSuggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputMessage(suggestion)}
                    className="text-xs px-3 py-1.5 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-full transition-colors font-medium border border-primary-100/50"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <form
            onSubmit={handleSendMessage}
            className="p-3 sm:p-4 bg-white border-t border-gray-100 shrink-0"
          >
            <div className="flex gap-2 items-center">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ketik pesan Anda..."
                className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-400/50 focus:border-primary-300 text-sm text-gray-800 placeholder-gray-400 bg-gray-50 transition-all"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="bg-gradient-to-br from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 disabled:from-gray-300 disabled:to-gray-400 text-white p-3 rounded-xl transition-all transform hover:scale-105 active:scale-95 shadow-lg shadow-primary-600/25 disabled:shadow-none"
              >
                <FiSend size={18} />
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Toggle Button */}
      <button
        onClick={() => {
          if (isOpen) {
            handleClose();
          } else {
            setIsOpen(true);
          }
        }}
        className={`bg-gradient-to-br from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white p-4 sm:p-5 rounded-2xl shadow-2xl shadow-primary-600/30 transition-all transform hover:scale-110 active:scale-95 ${
          !isOpen ? 'animate-pulse-glow' : ''
        }`}
        aria-label="Toggle chatbot"
      >
        {isOpen ? <FiX size={24} /> : <FiMessageCircle size={24} />}
      </button>
    </div>
  );
};

export default FloatingChatbot;

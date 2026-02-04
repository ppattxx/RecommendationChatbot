/**
 * Floating Chatbot Widget Component
 * Komponen chat dengan fitur:
 * - Chat history persistence via localStorage & backend
 * - Integration dengan PersonalizationContext
 * - Loading skeleton untuk smooth UX
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { FiMessageCircle, FiX, FiSend, FiRefreshCw } from 'react-icons/fi';
import { chatAPI } from '../services/api';
import { usePersonalization } from '../contexts/PersonalizationContext';

// Storage key for chat messages
const CHAT_STORAGE_KEY = 'chat_history';

/**
 * Loading Skeleton untuk messages
 */
const MessageSkeleton = () => (
  <div className="space-y-4 animate-pulse">
    {[1, 2, 3].map((i) => (
      <div key={i} className={`flex items-end gap-2 ${i % 2 === 0 ? 'justify-end' : 'justify-start'}`}>
        {i % 2 !== 0 && <div className="w-8 h-8 bg-gray-200 rounded-full"></div>}
        <div className={`max-w-[75%] rounded-2xl p-3.5 ${
          i % 2 === 0 ? 'bg-gray-300' : 'bg-gray-100'
        }`}>
          <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-20"></div>
        </div>
      </div>
    ))}
  </div>
);

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Get context values
  const { 
    sessionId, 
    deviceToken, 
    updateSession, 
    refreshPersonalization,
    resetAllData 
  } = usePersonalization();

  // Scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      try {
        localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
      } catch (error) {
        console.error('Error saving chat to localStorage:', error);
      }
    }
  }, [messages]);

  // Load chat history when chatbot opens for the first time
  useEffect(() => {
    if (isOpen && !historyLoaded) {
      loadChatHistory();
    }
  }, [isOpen, historyLoaded]);

  /**
   * Load chat history from localStorage first, then sync with backend
   */
  const loadChatHistory = async () => {
    setIsLoadingHistory(true);
    
    try {
      // Step 1: Try to load from localStorage first (instant display)
      const localHistory = localStorage.getItem(CHAT_STORAGE_KEY);
      if (localHistory) {
        const parsedHistory = JSON.parse(localHistory);
        if (Array.isArray(parsedHistory) && parsedHistory.length > 0) {
          // Convert timestamps to Date objects
          const formattedHistory = parsedHistory.map(msg => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }));
          setMessages(formattedHistory);
          setHistoryLoaded(true);
          setIsLoadingHistory(false);
          return;
        }
      }

      // Step 2: If no local history and we have a session, fetch from backend
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

      // Step 3: No history found, initialize with welcome message
      initializeNewChat();
      
    } catch (error) {
      console.error('Error loading chat history:', error);
      initializeNewChat();
    } finally {
      setIsLoadingHistory(false);
      setHistoryLoaded(true);
    }
  };

  /**
   * Initialize new chat with welcome message
   */
  const initializeNewChat = async () => {
    setIsLoading(true);
    try {
      // Create new session with greeting
      const response = await chatAPI.sendMessage('halo', null, deviceToken);
      
      if (response.success) {
        // Update session in context
        if (response.data.session_id) {
          updateSession(response.data.session_id);
        }
        
        const welcomeMessage = {
          type: 'bot',
          text: response.data.bot_response,
          timestamp: new Date(response.data.timestamp),
          synced: true,
        };
        
        setMessages([welcomeMessage]);
      } else {
        // Fallback welcome message
        setMessages([{
          type: 'bot',
          text: 'Halo! Saya siap membantu Anda mencari rekomendasi restoran di Lombok. Silakan ceritakan preferensi makanan Anda.',
          timestamp: new Date(),
          synced: false,
        }]);
      }
    } catch (error) {
      console.error('Error initializing chat:', error);
      setMessages([{
        type: 'bot',
        text: 'Halo! Saya siap membantu Anda mencari rekomendasi restoran di Lombok. Silakan ceritakan preferensi makanan Anda.',
        timestamp: new Date(),
        synced: false,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle sending message
   */
  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;

    // Add user message to chat immediately
    const userMessage = {
      type: 'user',
      text: inputMessage,
      timestamp: new Date(),
      synced: false,
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(
        inputMessage,
        sessionId,
        deviceToken
      );

      if (response.success) {
        // Update session if new
        if (response.data.session_id && response.data.session_id !== sessionId) {
          updateSession(response.data.session_id);
        }

        // Add bot response
        const botMessage = {
          type: 'bot',
          text: response.data.bot_response,
          timestamp: new Date(response.data.timestamp),
          synced: true,
        };
        
        setMessages((prev) => {
          // Mark user message as synced
          const updated = prev.map(msg => 
            msg === userMessage ? { ...msg, synced: true } : msg
          );
          return [...updated, botMessage];
        });

        // Trigger async personalization refresh (no page reload)
        // This updates recommendations in the background
        setTimeout(() => {
          refreshPersonalization();
        }, 1000);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'bot',
        text: 'Maaf, terjadi kesalahan. Silakan coba lagi.',
        timestamp: new Date(),
        synced: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle reset all history
   */
  const handleResetHistory = async () => {
    if (confirm('Yakin ingin mereset SEMUA riwayat chat dan preferensi? Ini akan menghapus semua data dan tidak bisa dikembalikan!')) {
      try {
        // Use context's resetAllData which handles everything
        const success = await resetAllData();
        
        if (success) {
          // Reset local state
          setMessages([]);
          setHistoryLoaded(false);
          localStorage.removeItem(CHAT_STORAGE_KEY);
          
          alert('Berhasil menghapus semua riwayat!');
          
          // Reload page to reset all states
          window.location.reload();
        } else {
          alert('Gagal mereset history. Silakan coba lagi.');
        }
      } catch (error) {
        console.error('Error resetting history:', error);
        alert('Gagal mereset history. Silakan coba lagi.');
      }
    }
  };

  /**
   * Format timestamp for display
   */
  const formatTime = (date) => {
    if (!(date instanceof Date)) {
      date = new Date(date);
    }
    return new Intl.DateTimeFormat('id-ID', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-[420px] h-[650px] bg-white rounded-2xl shadow-2xl flex flex-col animate-slide-up border border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-5 rounded-t-2xl flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="bg-white/20 p-2 rounded-full">
                <FiMessageCircle size={24} />
              </div>
              <div>
                <h3 className="font-bold text-lg">Chatbot Rekomendasi</h3>
                <p className="text-xs text-primary-100 flex items-center gap-1">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  Online • Siap membantu
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleResetHistory}
                className="hover:bg-white/20 p-2 rounded-lg transition-colors"
                title="Reset Semua History"
              >
                <FiRefreshCw size={18} />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="hover:bg-white/20 p-2 rounded-lg transition-colors"
              >
                <FiX size={22} />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-gradient-to-b from-gray-50 to-white">
            {/* Loading History Skeleton */}
            {isLoadingHistory && <MessageSkeleton />}
            
            {/* Empty State */}
            {!isLoadingHistory && messages.length === 0 && !isLoading && (
              <div className="text-center text-gray-400 mt-8">
                <FiMessageCircle size={48} className="mx-auto mb-3 opacity-50" />
                <p className="text-sm">Belum ada percakapan</p>
                <p className="text-xs mt-1">Mulai chat untuk rekomendasi restoran</p>
              </div>
            )}
            
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex items-end gap-2 ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.type === 'bot' && (
                  <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mb-1">
                    <span className="text-primary-700 text-sm font-semibold">AI</span>
                  </div>
                )}
                <div
                  className={`max-w-[75%] rounded-2xl p-3.5 shadow-sm ${
                    message.type === 'user'
                      ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-br-sm'
                      : 'bg-white text-gray-800 border border-gray-100 rounded-bl-sm'
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                    {message.text}
                  </p>
                  <p
                    className={`text-xs mt-2 ${
                      message.type === 'user'
                        ? 'text-primary-100'
                        : 'text-gray-400'
                    }`}
                  >
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-end gap-2 justify-start">
                <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mb-1">
                  <span className="text-primary-700 text-sm font-semibold">AI</span>
                </div>
                <div className="bg-white rounded-2xl rounded-bl-sm p-4 shadow-sm border border-gray-100">
                  <div className="flex space-x-2">
                    <div className="w-2.5 h-2.5 bg-primary-400 rounded-full animate-bounce"></div>
                    <div className="w-2.5 h-2.5 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2.5 h-2.5 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestions (Optional) */}
          {messages.length === 1 && !isLoading && (
            <div className="px-5 pb-2">
              <p className="text-xs text-gray-500 mb-2"> Coba tanyakan:</p>
              <div className="flex flex-wrap gap-2">
                {['Pizza di Kuta', 'Seafood romantis', 'Cafe dengan WiFi'].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setInputMessage(suggestion);
                    }}
                    className="text-xs px-3 py-1.5 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-full transition-colors"
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
            className="p-4 bg-white border-t border-gray-100 rounded-b-2xl"
          >
            <div className="flex gap-2 items-center">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ketik pesan Anda..."
                className="flex-1 px-4 py-3 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent text-gray-800 placeholder-gray-400 bg-gray-50"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 disabled:from-gray-300 disabled:to-gray-400 text-white p-3.5 rounded-full transition-all transform hover:scale-105 active:scale-95 shadow-md"
              >
                <FiSend size={20} />
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white p-5 rounded-full shadow-2xl transition-all transform hover:scale-110 active:scale-95 hover:shadow-primary-300/50"
      >
        {isOpen ? <FiX size={28} /> : <FiMessageCircle size={28} />}
      </button>
    </div>
  );
};

export default FloatingChatbot;

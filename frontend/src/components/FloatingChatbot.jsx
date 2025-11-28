/**
 * Floating Chatbot Widget Component
 * Komponen chat yang bisa dibuka-tutup di pojok kanan bawah
 */
import { useState, useEffect, useRef } from 'react';
import { FiMessageCircle, FiX, FiSend } from 'react-icons/fi';
import { chatAPI } from '../services/api';

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  // Generate device token (simpan di localStorage)
  const getDeviceToken = () => {
    let token = localStorage.getItem('device_token');
    if (!token) {
      token = `dev_${Math.random().toString(36).substring(2, 15)}`;
      localStorage.setItem('device_token', token);
    }
    return token;
  };

  // Scroll to bottom ketika ada pesan baru
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat saat dibuka pertama kali
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      initializeChat();
    }
  }, [isOpen]);

  const initializeChat = async () => {
    setIsLoading(true);
    try {
      const deviceToken = getDeviceToken();
      const response = await chatAPI.sendMessage('', null, deviceToken);
      
      if (response.success) {
        setSessionId(response.data.session_id);
        setMessages([
          {
            type: 'bot',
            text: response.data.bot_response,
            timestamp: new Date(response.data.timestamp),
          },
        ]);
      }
    } catch (error) {
      console.error('Error initializing chat:', error);
      setMessages([
        {
          type: 'bot',
          text: 'Maaf, terjadi kesalahan. Silakan coba lagi.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;

    // Tambahkan pesan user ke chat
    const userMessage = {
      type: 'user',
      text: inputMessage,
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const deviceToken = getDeviceToken();
      const response = await chatAPI.sendMessage(
        inputMessage,
        sessionId,
        deviceToken
      );

      if (response.success) {
        // Update session ID jika baru
        if (response.data.session_id) {
          setSessionId(response.data.session_id);
        }

        // Tambahkan response bot
        const botMessage = {
          type: 'bot',
          text: response.data.bot_response,
          timestamp: new Date(response.data.timestamp),
        };
        
        setMessages((prev) => [...prev, botMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'bot',
        text: 'Maaf, terjadi kesalahan. Silakan coba lagi.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date) => {
    return new Intl.DateTimeFormat('id-ID', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col animate-slide-up">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-4 rounded-t-2xl flex justify-between items-center">
            <div>
              <h3 className="font-bold text-lg">Chatbot Rekomendasi</h3>
              <p className="text-xs text-primary-100">Cari restoran favoritmu!</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-primary-500 p-2 rounded-full transition-colors"
            >
              <FiX size={24} />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[75%] rounded-2xl p-3 ${
                    message.type === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-white text-gray-800 shadow-md'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap break-words">
                    {message.text}
                  </p>
                  <p
                    className={`text-xs mt-1 ${
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
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl p-3 shadow-md">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form
            onSubmit={handleSendMessage}
            className="p-4 bg-white border-t rounded-b-2xl"
          >
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ketik pesan Anda..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-800"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white p-3 rounded-full transition-colors"
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
        className="bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white p-4 rounded-full shadow-2xl transition-all transform hover:scale-110"
      >
        {isOpen ? <FiX size={28} /> : <FiMessageCircle size={28} />}
      </button>
    </div>
  );
};

export default FloatingChatbot;

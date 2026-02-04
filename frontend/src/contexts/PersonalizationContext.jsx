/**
 * Personalization Context
 * State management untuk seamless personalization tanpa page refresh
 * Menangani preferences, recommendations, dan chat history
 */
import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { preferencesAPI, recommendationsAPI, chatAPI } from '../services/api';

// Context
const PersonalizationContext = createContext(null);

// Storage keys
const STORAGE_KEYS = {
  SESSION_ID: 'session_id',
  DEVICE_TOKEN: 'device_token',
  CHAT_HISTORY: 'chat_history',
  PREFERENCES_CACHE: 'preferences_cache',
  LAST_SYNC: 'last_sync_timestamp',
};

/**
 * Provider Component
 * Wrap aplikasi dengan provider ini untuk akses global ke personalization state
 */
export const PersonalizationProvider = ({ children }) => {
  // User identification
  const [sessionId, setSessionId] = useState(() => localStorage.getItem(STORAGE_KEYS.SESSION_ID));
  const [deviceToken, setDeviceToken] = useState(() => {
    let token = localStorage.getItem(STORAGE_KEYS.DEVICE_TOKEN);
    if (!token) {
      token = `web_${Math.random().toString(36).substring(2, 11)}`;
      localStorage.setItem(STORAGE_KEYS.DEVICE_TOKEN, token);
    }
    return token;
  });

  // Data states
  const [preferences, setPreferences] = useState(null);
  const [topRecommendations, setTopRecommendations] = useState([]);
  const [chatHistory, setChatHistory] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // Loading states
  const [isLoadingPreferences, setIsLoadingPreferences] = useState(false);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Error states
  const [error, setError] = useState(null);

  // Sync chat history to localStorage whenever it changes
  useEffect(() => {
    if (chatHistory.length > 0) {
      localStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(chatHistory));
    }
  }, [chatHistory]);

  // Update session ID in localStorage
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(STORAGE_KEYS.SESSION_ID, sessionId);
    }
  }, [sessionId]);

  /**
   * Fetch user preferences dari backend
   * @returns {Promise<Object|null>} preferences data atau null jika error
   */
  const fetchPreferences = useCallback(async () => {
    setIsLoadingPreferences(true);
    setError(null);
    try {
      const response = await preferencesAPI.getUserPreferences({
        session_id: sessionId || undefined,
        device_token: deviceToken || undefined,
      });
      if (response.success) {
        setPreferences(response.data);
        return response.data;
      }
      return null;
    } catch (err) {
      console.error('Error fetching preferences:', err);
      setError('Gagal memuat preferensi');
      return null;
    } finally {
      setIsLoadingPreferences(false);
    }
  }, [sessionId, deviceToken]);

  /**
   * Fetch Top 5 recommendations berdasarkan personalisasi
   * Backend akan menghitung cosine similarity dan mengembalikan 5 terbaik
   * @returns {Promise<Array>} array of top recommendations
   */
  const fetchTopRecommendations = useCallback(async () => {
    setIsLoadingRecommendations(true);
    setError(null);
    try {
      const response = await recommendationsAPI.getRecommendations({
        device_token: deviceToken,
        session_id: sessionId || undefined,
        top_n: 5, // Request top 5 only for personalized section
        personalized: true,
      });
      if (response.success && response.data?.restaurants) {
        setTopRecommendations(response.data.restaurants);
        return response.data.restaurants;
      }
      return [];
    } catch (err) {
      console.error('Error fetching top recommendations:', err);
      setError('Gagal memuat rekomendasi');
      return [];
    } finally {
      setIsLoadingRecommendations(false);
    }
  }, [deviceToken, sessionId]);

  /**
   * Fetch chat history dari backend (untuk persistence)
   * Merge dengan local storage dan update state
   * @returns {Promise<Array>} chat history messages
   */
  const fetchChatHistory = useCallback(async () => {
    if (!sessionId) {
      return chatHistory;
    }
    
    setIsLoadingHistory(true);
    try {
      const response = await chatAPI.getChatHistory(sessionId);
      if (response.success && response.data?.messages) {
        // Convert backend format to frontend format
        const backendMessages = [];
        response.data.messages.forEach((msg) => {
          // Add user message
          if (msg.user_message) {
            backendMessages.push({
              type: 'user',
              text: msg.user_message,
              timestamp: new Date(msg.timestamp),
              synced: true,
            });
          }
          // Add bot response
          if (msg.bot_response) {
            backendMessages.push({
              type: 'bot',
              text: msg.bot_response,
              timestamp: new Date(msg.timestamp),
              synced: true,
            });
          }
        });

        // Update state with backend data
        if (backendMessages.length > 0) {
          setChatHistory(backendMessages);
          localStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(backendMessages));
        }
        return backendMessages;
      }
      return chatHistory;
    } catch (err) {
      console.error('Error fetching chat history:', err);
      // Return local storage data as fallback
      return chatHistory;
    } finally {
      setIsLoadingHistory(false);
    }
  }, [sessionId, chatHistory]);

  /**
   * Add message to chat history (local state + localStorage)
   * @param {Object} message - { type: 'user'|'bot', text: string, timestamp: Date }
   */
  const addChatMessage = useCallback((message) => {
    const newMessage = {
      ...message,
      timestamp: message.timestamp || new Date(),
      synced: false,
    };
    setChatHistory((prev) => [...prev, newMessage]);
  }, []);

  /**
   * Clear all chat history (local + backend)
   */
  const clearChatHistory = useCallback(async () => {
    try {
      // Clear backend
      if (deviceToken || sessionId) {
        await chatAPI.resetChatHistory(deviceToken, sessionId);
      }
      
      // Clear local
      setChatHistory([]);
      localStorage.removeItem(STORAGE_KEYS.CHAT_HISTORY);
      
      return true;
    } catch (err) {
      console.error('Error clearing chat history:', err);
      return false;
    }
  }, [deviceToken, sessionId]);

  /**
   * Update session ID (called after new chat session created)
   * Triggers async refresh of preferences and recommendations
   * @param {string} newSessionId 
   */
  const updateSession = useCallback((newSessionId) => {
    setSessionId(newSessionId);
    localStorage.setItem(STORAGE_KEYS.SESSION_ID, newSessionId);
    
    // Async refresh - no page reload needed
    setTimeout(() => {
      fetchPreferences();
      fetchTopRecommendations();
    }, 500);
  }, [fetchPreferences, fetchTopRecommendations]);

  /**
   * Trigger refresh of all personalization data
   * Called after chat interaction that might change preferences
   */
  const refreshPersonalization = useCallback(async () => {
    const results = await Promise.all([
      fetchPreferences(),
      fetchTopRecommendations(),
    ]);
    return results;
  }, [fetchPreferences, fetchTopRecommendations]);

  /**
   * Reset all personalization data
   */
  const resetAllData = useCallback(async () => {
    try {
      // Clear backend data
      await chatAPI.resetAllChatHistory();
      
      // Clear all local storage
      Object.values(STORAGE_KEYS).forEach((key) => {
        localStorage.removeItem(key);
      });
      
      // Reset states
      setSessionId(null);
      setPreferences(null);
      setTopRecommendations([]);
      setChatHistory([]);
      
      // Generate new device token
      const newToken = `web_${Math.random().toString(36).substring(2, 11)}`;
      setDeviceToken(newToken);
      localStorage.setItem(STORAGE_KEYS.DEVICE_TOKEN, newToken);
      
      return true;
    } catch (err) {
      console.error('Error resetting all data:', err);
      return false;
    }
  }, []);

  // Context value
  const value = {
    // Identification
    sessionId,
    deviceToken,
    updateSession,
    
    // Preferences
    preferences,
    isLoadingPreferences,
    fetchPreferences,
    
    // Recommendations
    topRecommendations,
    isLoadingRecommendations,
    fetchTopRecommendations,
    
    // Chat History
    chatHistory,
    isLoadingHistory,
    fetchChatHistory,
    addChatMessage,
    clearChatHistory,
    
    // Global actions
    refreshPersonalization,
    resetAllData,
    
    // Error state
    error,
    clearError: () => setError(null),
  };

  return (
    <PersonalizationContext.Provider value={value}>
      {children}
    </PersonalizationContext.Provider>
  );
};

/**
 * Custom hook untuk menggunakan PersonalizationContext
 * @returns {Object} context value
 * @throws {Error} jika digunakan di luar provider
 */
export const usePersonalization = () => {
  const context = useContext(PersonalizationContext);
  if (!context) {
    throw new Error('usePersonalization must be used within PersonalizationProvider');
  }
  return context;
};

export default PersonalizationContext;

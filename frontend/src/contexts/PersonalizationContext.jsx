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

export const PersonalizationProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem(STORAGE_KEYS.SESSION_ID));
  const [deviceToken, setDeviceToken] = useState(() => {
    let token = localStorage.getItem(STORAGE_KEYS.DEVICE_TOKEN);
    if (!token) {
      token = `web_${Math.random().toString(36).substring(2, 11)}`;
      localStorage.setItem(STORAGE_KEYS.DEVICE_TOKEN, token);
    }
    return token;
  });

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

  const [isLoadingPreferences, setIsLoadingPreferences] = useState(false);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
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

  const fetchChatHistory = useCallback(async () => {
    if (!sessionId) {
      return chatHistory;
    }

    setIsLoadingHistory(true);
    try {
      const response = await chatAPI.getChatHistory(sessionId);
      if (response.success && response.data?.messages) {
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

  const addChatMessage = useCallback((message) => {
    const newMessage = {
      ...message,
      timestamp: message.timestamp || new Date(),
      synced: false,
    };
    setChatHistory((prev) => [...prev, newMessage]);
  }, []);

  const clearChatHistory = useCallback(async () => {
    try {
      if (deviceToken || sessionId) {
        await chatAPI.resetChatHistory(deviceToken, sessionId);
      }

      setChatHistory([]);
      localStorage.removeItem(STORAGE_KEYS.CHAT_HISTORY);

      return true;
    } catch (err) {
      console.error('Error clearing chat history:', err);
      return false;
    }
  }, [deviceToken, sessionId]);

  const updateSession = useCallback((newSessionId) => {
    setSessionId(newSessionId);
    localStorage.setItem(STORAGE_KEYS.SESSION_ID, newSessionId);

    setTimeout(() => {
      fetchPreferences();
      fetchTopRecommendations();
    }, 500);
  }, [fetchPreferences, fetchTopRecommendations]);

  const refreshPersonalization = useCallback(async () => {
    const results = await Promise.all([
      fetchPreferences(),
      fetchTopRecommendations(),
    ]);
    return results;
  }, [fetchPreferences, fetchTopRecommendations]);

  const resetAllData = useCallback(async () => {
    try {
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

export const usePersonalization = () => {
  const context = useContext(PersonalizationContext);
  if (!context) {
    throw new Error('usePersonalization must be used within PersonalizationProvider');
  }
  return context;
};

export default PersonalizationContext;

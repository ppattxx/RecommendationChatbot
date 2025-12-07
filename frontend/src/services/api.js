/**
 * API Service untuk komunikasi dengan Flask Backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance dengan default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
});

// Request interceptor untuk logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor untuk error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response || error);
    return Promise.reject(error);
  }
);

/**
 * Chat API
 */
export const chatAPI = {
  /**
   * Send message to chatbot
   * @param {string} message - User message
   * @param {string} sessionId - Session ID (optional)
   * @param {string} deviceToken - Device token (optional)
   * @returns {Promise} Response from chatbot
   */
  sendMessage: async (message, sessionId = null, deviceToken = null) => {
    try {
      const response = await apiClient.post('/chat', {
        message,
        session_id: sessionId,
        device_token: deviceToken,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },

  /**
   * Get chat history
   * @param {string} sessionId - Session ID
   * @returns {Promise} Chat history
   */
  getChatHistory: async (sessionId) => {
    try {
      const response = await apiClient.get(`/chat/history/${sessionId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },

  /**
   * Reset chat history
   * @param {string} deviceToken - Device token (optional)
   * @param {string} sessionId - Session ID (optional)
   * @returns {Promise} Reset result
   */
  resetChatHistory: async (deviceToken = null, sessionId = null) => {
    try {
      const response = await apiClient.delete('/chat/reset', {
        data: {
          device_token: deviceToken,
          session_id: sessionId,
        }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },

  /**
   * Reset ALL chat history (WARNING: deletes all data)
   * @returns {Promise} Reset result
   */
  resetAllChatHistory: async () => {
    try {
      const response = await apiClient.delete('/chat/reset-all');
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },
};

/**
 * Preferences API
 */
export const preferencesAPI = {
  /**
   * Get user preferences analysis
   * @param {Object} params - Query parameters
   * @returns {Promise} Preferences data
   */
  getUserPreferences: async (params = {}) => {
    try {
      const response = await apiClient.get('/user-preferences', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },

  /**
   * Get preferences summary
   * @returns {Promise} Summary data
   */
  getPreferencesSummary: async () => {
    try {
      const response = await apiClient.get('/user-preferences/summary');
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },
};

/**
 * Recommendations API
 */
export const recommendationsAPI = {
  /**
   * Get personalized recommendations
   * @param {Object} params - Query parameters
   * @returns {Promise} Recommendations data
   */
  getRecommendations: async (params = {}) => {
    try {
      const response = await apiClient.get('/recommendations', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },

  /**
   * Get available categories
   * @returns {Promise} Categories data
   */
  getCategories: async () => {
    try {
      const response = await apiClient.get('/recommendations/categories');
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },

  /**
   * Get trending restaurants
   * @param {number} limit - Number of results
   * @returns {Promise} Trending data
   */
  getTrending: async (limit = 5) => {
    try {
      const response = await apiClient.get(`/recommendations/trending?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },
};

/**
 * Health check
 */
export const healthAPI = {
  check: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },
};

export default apiClient;

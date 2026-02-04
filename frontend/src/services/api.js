/**
 * API Service untuk komunikasi dengan Flask Backend
 */
import axios from 'axios';

// Use relative URL to leverage Vite proxy in development
// In production, set VITE_API_URL environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

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
   * Get chat history for a session
   * @param {string} sessionId - Session ID
   * @param {Object} params - Optional pagination params
   * @returns {Promise} Chat history with pagination
   */
  getChatHistory: async (sessionId, params = {}) => {
    try {
      const response = await apiClient.get(`/chat/history/${sessionId}`, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },

  /**
   * Get all chat history for a device (all sessions)
   * @param {string} deviceToken - Device token
   * @param {Object} params - Optional params (limit)
   * @returns {Promise} All sessions with messages
   */
  getChatHistoryByDevice: async (deviceToken, params = {}) => {
    try {
      const response = await apiClient.get(`/chat/history/device/${deviceToken}`, { params });
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
   * Get personalized recommendations with pagination
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (default: 1)
   * @param {number} params.per_page - Items per page (default: 20, max: 100)
   * @param {string} params.session_id - Session ID for personalization
   * @param {string} params.device_token - Device token for personalization
   * @param {string} params.category - Filter by category
   * @returns {Promise} Paginated recommendations data with metadata
   * Response format:
   * {
   *   success: true,
   *   data: {
   *     restaurants: [...],
   *     total: 1163,
   *     page: 1,
   *     per_page: 20,
   *     total_pages: 59,
   *     has_next: true,
   *     has_prev: false,
   *     personalized: false
   *   }
   * }
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
   * Get Top 5 recommendations using Cosine Similarity
   * Sorted by similarity score with rating/review as tie-breaker
   * @param {Object} params - Query parameters
   * @param {string} params.session_id - Session ID for personalization
   * @param {string} params.device_token - Device token for personalization
   * @param {string} params.query - Optional search query
   * @returns {Promise} Top 5 recommendations
   * Response format:
   * {
   *   success: true,
   *   data: {
   *     restaurants: [...],
   *     query: "...",
   *     personalized: true/false,
   *     algorithm: "cosine_similarity",
   *     tie_breaker: "rating_and_review_count"
   *   }
   * }
   */
  getTop5Recommendations: async (params = {}) => {
    try {
      const response = await apiClient.get('/recommendations/top5', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Network error' };
    }
  },

  /**
   * Get ALL ranked recommendations using Cosine Similarity with pagination
   * Sorted by similarity score with rating/review as tie-breaker
   * Top 5 will have is_top5=true flag for UI labeling
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (default: 1)
   * @param {number} params.limit - Items per page (default: 20, max: 100)
   * @param {string} params.session_id - Session ID for personalization
   * @param {string} params.device_token - Device token for personalization
   * @param {string} params.query - Optional search query
   * @returns {Promise} All ranked recommendations with pagination
   * Response format:
   * {
   *   success: true,
   *   data: {
   *     restaurants: [{ ...restaurantData, rank: 1, is_top5: true }, ...],
   *     pagination: { current_page, total_pages, total_items, ... },
   *     query: "...",
   *     personalized: true/false,
   *     algorithm: "cosine_similarity"
   *   }
   * }
   */
  getAllRankedRecommendations: async (params = {}) => {
    try {
      const response = await apiClient.get('/recommendations/all-ranked', { params });
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

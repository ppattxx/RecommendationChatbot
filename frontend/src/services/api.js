/**
 * API Service untuk komunikasi dengan Flask Backend.
 * Uses centralized error handler and structured logger.
 */
import axios from 'axios';
import { handleAPIError } from '../utils/errorHandler';
import { createLogger } from '../utils/logger';

const log = createLogger('API');

// Use relative URL to leverage Vite proxy in development
// In production, set VITE_API_URL environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Create axios instance dengan default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
});

// ─── Interceptors ─────────────────────────────────────────────

apiClient.interceptors.request.use(
  (config) => {
    log.debug(`→ ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    log.error('Request setup failed', error);
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    const reqId = response.headers?.['x-request-id'] || '';
    log.debug(
      `← ${response.status} ${response.config?.url}`,
      reqId ? { requestId: reqId } : null
    );
    return response;
  },
  (error) => {
    // Let individual callers handle via handleAPIError
    return Promise.reject(error);
  }
);


// ─── Helper: safe API call wrapper ────────────────────────────

async function apiCall(fn) {
  try {
    const response = await fn();
    return response.data;
  } catch (error) {
    throw handleAPIError(error);
  }
}


// ─── Chat API ─────────────────────────────────────────────────

export const chatAPI = {
  /**
   * Send message to chatbot
   * @param {string} message - User message
   * @param {string} sessionId - Session ID (optional)
   * @param {string} deviceToken - Device token (optional)
   */
  sendMessage: (message, sessionId = null, deviceToken = null) =>
    apiCall(() => apiClient.post('/chat', {
      message,
      session_id: sessionId,
      device_token: deviceToken,
    })),

  /**
   * Get chat history for a session
   * @param {string} sessionId
   * @param {Object} params - Pagination params
   */
  getChatHistory: (sessionId, params = {}) =>
    apiCall(() => apiClient.get(`/chat/history/${sessionId}`, { params })),

  /**
   * Get all chat history for a device (all sessions)
   * @param {string} deviceToken
   * @param {Object} params - { limit }
   */
  getChatHistoryByDevice: (deviceToken, params = {}) =>
    apiCall(() => apiClient.get(`/chat/history/device/${deviceToken}`, { params })),

  /**
   * Reset chat history
   * @param {string} deviceToken
   * @param {string} sessionId
   */
  resetChatHistory: (deviceToken = null, sessionId = null) =>
    apiCall(() => apiClient.delete('/chat/reset', {
      data: { device_token: deviceToken, session_id: sessionId }
    })),

  /** Reset ALL chat history (WARNING: deletes all data) */
  resetAllChatHistory: () =>
    apiCall(() => apiClient.delete('/chat/reset-all')),
};


// ─── Preferences API ─────────────────────────────────────────

export const preferencesAPI = {
  /** Get user preferences analysis */
  getUserPreferences: (params = {}) =>
    apiCall(() => apiClient.get('/user-preferences', { params })),

  /** Get preferences summary */
  getPreferencesSummary: () =>
    apiCall(() => apiClient.get('/user-preferences/summary')),
};


// ─── Recommendations API ──────────────────────────────────────

export const recommendationsAPI = {
  /**
   * Get personalized recommendations with pagination
   * @param {Object} params - { page, per_page, session_id, device_token, category }
   */
  getRecommendations: (params = {}) =>
    apiCall(() => apiClient.get('/recommendations', { params })),

  /**
   * Get Top 5 recommendations using Cosine Similarity
   * @param {Object} params - { session_id, device_token, query }
   */
  getTop5Recommendations: (params = {}) =>
    apiCall(() => apiClient.get('/recommendations/top5', { params })),

  /**
   * Get ALL ranked recommendations with pagination
   * @param {Object} params - { page, limit, session_id, device_token, query }
   */
  getAllRankedRecommendations: (params = {}) =>
    apiCall(() => apiClient.get('/recommendations/all-ranked', { params })),

  /** Get available categories */
  getCategories: () =>
    apiCall(() => apiClient.get('/recommendations/categories')),

  /**
   * Get trending restaurants
   * @param {number} limit
   */
  getTrending: (limit = 5) =>
    apiCall(() => apiClient.get(`/recommendations/trending?limit=${limit}`)),
};


// ─── Health API ───────────────────────────────────────────────

export const healthAPI = {
  check: () => apiCall(() => apiClient.get('/health')),
};

export default apiClient;

import axios from 'axios';
import { handleAPIError } from '../utils/errorHandler';
import { createLogger } from '../utils/logger';

const log = createLogger('API');

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
});

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
    return Promise.reject(error);
  }
);

async function apiCall(fn) {
  try {
    const response = await fn();
    return response.data;
  } catch (error) {
    throw handleAPIError(error);
  }
}

export const chatAPI = {
  sendMessage: (message, sessionId = null, deviceToken = null) =>
    apiCall(() => apiClient.post('/chat', {
      message,
      session_id: sessionId,
      device_token: deviceToken,
    })),

  getChatHistory: (sessionId, params = {}) =>
    apiCall(() => apiClient.get(`/chat/history/${sessionId}`, { params })),

  getChatHistoryByDevice: (deviceToken, params = {}) =>
    apiCall(() => apiClient.get(`/chat/history/device/${deviceToken}`, { params })),

  resetChatHistory: (deviceToken = null, sessionId = null) =>
    apiCall(() => apiClient.delete('/chat/reset', {
      data: { device_token: deviceToken, session_id: sessionId }
    })),

  resetAllChatHistory: () =>
    apiCall(() => apiClient.delete('/chat/reset-all')),
};



export const preferencesAPI = {
  getUserPreferences: (params = {}) =>
    apiCall(() => apiClient.get('/user-preferences', { params })),

  getPreferencesSummary: () =>
    apiCall(() => apiClient.get('/user-preferences/summary')),
};



export const recommendationsAPI = {
  getRecommendations: (params = {}) =>
    apiCall(() => apiClient.get('/recommendations', { params })),

  getTop5Recommendations: (params = {}) =>
    apiCall(() => apiClient.get('/recommendations/top5', { params })),

  getAllRankedRecommendations: (params = {}) =>
    apiCall(() => apiClient.get('/recommendations/all-ranked', { params })),

  getProfileDebug: (params = {}) =>
    apiCall(() => apiClient.get('/recommendations/profile-debug', { params })),

  getCategories: () =>
    apiCall(() => apiClient.get('/recommendations/categories')),


  getTrending: (limit = 5) =>
    apiCall(() => apiClient.get(`/recommendations/trending?limit=${limit}`)),
};



export const healthAPI = {
  check: () => apiCall(() => apiClient.get('/health')),
};

export default apiClient;

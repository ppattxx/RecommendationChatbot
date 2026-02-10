/**
 * Centralized API error handler.
 * Normalizes errors from Axios into a consistent shape
 * and provides user-friendly messages.
 */
import { createLogger } from '../utils/logger';

const log = createLogger('APIError');

/**
 * @typedef {Object} APIErrorResult
 * @property {boolean} success - Always false
 * @property {string} error   - Human-readable error message
 * @property {number} status  - HTTP status code (0 = network)
 * @property {string|null} requestId - Server-side X-Request-ID
 */

/**
 * Normalize any Axios error into a consistent APIErrorResult.
 * @param {Error} error - Axios error object
 * @returns {APIErrorResult}
 */
export function handleAPIError(error) {
    // Server responded with an error status
    if (error.response) {
        const { status, data, headers } = error.response;
        const requestId = headers?.['x-request-id'] || null;
        const message = data?.error || data?.message || _statusMessage(status);

        log.warn(`${status} ${message}`, { requestId, url: error.config?.url });

        return {
            success: false,
            error: message,
            status,
            requestId,
        };
    }

    // Request was made but no response (network error / timeout)
    if (error.request) {
        const isTimeout = error.code === 'ECONNABORTED';
        const message = isTimeout
            ? 'Koneksi timeout. Silakan coba lagi.'
            : 'Tidak dapat terhubung ke server.';

        log.error(message, { code: error.code, url: error.config?.url });

        return {
            success: false,
            error: message,
            status: 0,
            requestId: null,
        };
    }

    // Unexpected error
    log.error('Unexpected error', error);
    return {
        success: false,
        error: 'Terjadi kesalahan yang tidak terduga.',
        status: 0,
        requestId: null,
    };
}

function _statusMessage(status) {
    const messages = {
        400: 'Permintaan tidak valid.',
        401: 'Sesi Anda telah berakhir. Silakan muat ulang.',
        403: 'Akses ditolak.',
        404: 'Data tidak ditemukan.',
        422: 'Data yang dikirim tidak valid.',
        429: 'Terlalu banyak permintaan. Silakan tunggu sebentar.',
        500: 'Terjadi kesalahan pada server.',
        502: 'Server sedang tidak tersedia.',
        503: 'Layanan sedang tidak tersedia.',
    };
    return messages[status] || `Error ${status}`;
}

export default handleAPIError;

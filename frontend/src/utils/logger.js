/**
 * Frontend Logger Utility
 * Replaces raw console.log/error with structured, level-aware logging.
 * In production, log level is 'warn' (suppresses debug/info).
 */

const LOG_LEVELS = { debug: 0, info: 1, warn: 2, error: 3, silent: 4 };

const currentLevel = import.meta.env.PROD ? 'warn' : 'debug';

function _log(level, tag, message, data = null) {
    if (LOG_LEVELS[level] < LOG_LEVELS[currentLevel]) return;

    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}] [${tag}]`;

    switch (level) {
        case 'error':
            console.error(prefix, message, data ?? '');
            break;
        case 'warn':
            console.warn(prefix, message, data ?? '');
            break;
        case 'info':
            console.info(prefix, message, data ?? '');
            break;
        default:
            console.debug(prefix, message, data ?? '');
    }
}

/**
 * Create a scoped logger instance.
 * @param {string} tag - Module/component name
 */
export function createLogger(tag) {
    return {
        debug: (msg, data) => _log('debug', tag, msg, data),
        info: (msg, data) => _log('info', tag, msg, data),
        warn: (msg, data) => _log('warn', tag, msg, data),
        error: (msg, data) => _log('error', tag, msg, data),
    };
}

export default createLogger;

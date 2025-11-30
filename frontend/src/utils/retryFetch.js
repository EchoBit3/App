/**
 * Utility para retry logic en llamadas a API
 */

/**
 * Realiza un fetch con retry automático en caso de error
 * @param {Function} fetchFn - Función que retorna una Promise
 * @param {Object} [options] - Opciones de configuración
 * @param {number} [options.maxRetries] - Número máximo de reintentos (default: 3)
 * @param {number} [options.retryDelay] - Delay base entre reintentos en ms (default: 1000)
 * @param {Function} [options.shouldRetry] - Función que determina si debe reintentar
 * @param {Function} [options.onRetry] - Callback ejecutado en cada reintento
 * @returns {Promise} Resultado del fetch exitoso
 */
export async function retryFetch(fetchFn, options) {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    shouldRetry = (error) => {
      // Retry en errores de red, timeouts, y 5xx server errors
      if (error instanceof TypeError) {
        return true; // Network error
      }
      if (error.response?.status >= 500) {
        return true; // Server error
      }
      if (error.code === 'ECONNABORTED') {
        return true; // Timeout
      }
      return false;
    },
    onRetry = null,
  } = options || {};

  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Intentar el fetch
      const result = await fetchFn();
      return result;
    } catch (error) {
      lastError = error;
      
      // Si es el último intento o no debe reintentar, lanzar el error
      if (attempt === maxRetries || !shouldRetry(error)) {
        throw error;
      }
      
      // Calcular delay con exponential backoff
      const delay = retryDelay * Math.pow(2, attempt);
      
      // Callback de reintento
      if (onRetry) {
        onRetry(attempt + 1, maxRetries, delay, error);
      }
      
      // Esperar antes de reintentar
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
}

/**
 * Wrapper para fetch nativo con retry
 * @param {string} url - URL del endpoint
 * @param {Object} [fetchOptions] - Opciones de fetch
 * @param {Object} [retryOptions] - Opciones de retry
 * @returns {Promise<Response>} Response del fetch
 */
export async function fetchWithRetry(url, fetchOptions, retryOptions) {
  return retryFetch(
    () => fetch(url, fetchOptions).then(async (response) => {
      if (!response.ok) {
        const error = new Error(`HTTP ${response.status}`);
        // @ts-ignore - Agregar response al error para retry logic
        error.response = response;
        throw error;
      }
      return response;
    }),
    retryOptions
  );
}

/**
 * Wrapper para axios con retry
 * @param {Function} axiosCall - Función que ejecuta la llamada axios
 * @param {Object} [retryOptions] - Opciones de retry
 * @returns {Promise} Resultado de la llamada axios
 */
export async function axiosWithRetry(axiosCall, retryOptions) {
  return retryFetch(axiosCall, retryOptions);
}

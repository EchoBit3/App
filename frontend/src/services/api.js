/**
 * Servicio para comunicarse con la API de De-Mystify
 */

import { fetchWithRetry } from '../utils/retryFetch';
import toast from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

/**
 * Obtiene el token de autenticación del localStorage
 * @returns {string|null} Token JWT o null
 */
const getAuthToken = () => {
  return localStorage.getItem('token');
};

/**
 * Obtiene los headers con autenticación
 * @returns {Object} Headers object
 */
const getAuthHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

export const api = {
  /**
   * Analiza una tarea ambigua usando la API (requiere autenticación)
   * @param {string} texto - Texto de la tarea a analizar
   * @returns {Promise<Object>} Resultado del análisis
   */
  async desambiguarTarea(texto) {
    let retryCount = 0;
    
    try {
      const response = await fetchWithRetry(
        `${API_URL}/api/desambiguar`,
        {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ texto }),
        },
        {
          maxRetries: 3,
          retryDelay: 1000,
          onRetry: (attempt, maxRetries, delay) => {
            retryCount = attempt;
            if (attempt === 1) {
              toast.loading(`Reintentando... (${attempt}/${maxRetries})`, {
                id: 'retry-toast',
                duration: delay,
              });
            } else {
              toast.loading(`Reintentando... (${attempt}/${maxRetries})`, {
                id: 'retry-toast',
                duration: delay,
              });
            }
          },
        }
      );

      // Limpiar toast de retry si existía
      if (retryCount > 0) {
        toast.dismiss('retry-toast');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      // Limpiar toast de retry
      toast.dismiss('retry-toast');
      
      // Network error (offline, CORS, etc)
      if (error instanceof TypeError) {
        throw new Error('No se pudo conectar con el servidor. Verifica que esté corriendo en http://localhost:8001');
      }
      
      // Server error con response
      if (error.response) {
        try {
          const errorData = await error.response.json();
          throw new Error(errorData.detail || 'Error al procesar la tarea');
        } catch (parseError) {
          throw new Error(`Error del servidor (${error.response.status})`);
        }
      }
      
      // Error genérico
      throw new Error(error.message || 'Error inesperado al procesar la tarea');
    }
  },

  /**
   * Obtiene ejemplos de tareas
   * @returns {Promise<Array>} Lista de ejemplos
   */
  async obtenerEjemplos() {
    try {
      const response = await fetchWithRetry(
        `${API_URL}/api/ejemplos`,
        {},
        {
          maxRetries: 2,
          retryDelay: 500,
        }
      );
      
      const data = await response.json();
      return data.ejemplos || [];
    } catch (error) {
      console.error('Error al obtener ejemplos:', error);
      return [];
    }
  },

  /**
   * Verifica el estado de la API
   * @returns {Promise<Object>} Estado del servidor
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_URL}/health`);
      return await response.json();
    } catch (error) {
      console.error('API no disponible:', error);
      return { status: 'offline' };
    }
  }
};

import { useState } from 'react';
import { api } from '../services/api';
import { VALIDATION_RULES, VALIDATION_MESSAGES } from '../constants/validation';

/**
 * Hook personalizado para manejar el análisis de tareas
 */
export const useTaskAnalyzer = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resultado, setResultado] = useState(null);

  /**
   * Valida el texto de entrada
   */
  const validateText = (texto, isAuthenticated) => {
    if (!isAuthenticated) {
      return VALIDATION_MESSAGES.AUTH_REQUIRED;
    }

    const textoLimpio = texto.trim();
    
    if (!textoLimpio) {
      return VALIDATION_MESSAGES.TASK_EMPTY;
    }

    if (textoLimpio.length < VALIDATION_RULES.TASK.MIN_LENGTH) {
      return VALIDATION_MESSAGES.TASK_TOO_SHORT;
    }

    if (texto.length > VALIDATION_RULES.TASK.MAX_LENGTH) {
      return VALIDATION_MESSAGES.TASK_TOO_LONG;
    }

    return null;
  };

  /**
   * Scroll suave a la sección de resultados
   */
  const scrollToResults = () => {
    setTimeout(() => {
      document.getElementById('resultados')?.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }, 100);
  };

  /**
   * Analiza una tarea usando la API
   */
  const analizarTarea = async (texto, isAuthenticated) => {
    const validationError = validateText(texto, isAuthenticated);
    
    if (validationError) {
      setError(validationError);
      return { success: false, requiresAuth: validationError === VALIDATION_MESSAGES.AUTH_REQUIRED };
    }

    setError('');
    setLoading(true);
    setResultado(null);

    try {
      const data = await api.desambiguarTarea(texto);
      setResultado(data);
      scrollToResults();
      return { success: true };
    } catch (err) {
      const errorMessage = err.message || VALIDATION_MESSAGES.API_ERROR;
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Carga un resultado anterior desde el historial
   */
  const cargarResultado = (consulta) => {
    const resultado = {
      pasos: consulta.pasos,
      ambiguedades: consulta.ambiguedades,
      preguntas_sugeridas: consulta.preguntas
    };
    setResultado(resultado);
    scrollToResults();
    return resultado;
  };

  /**
   * Limpia el estado
   */
  const limpiar = () => {
    setResultado(null);
    setError('');
  };

  return {
    loading,
    error,
    resultado,
    setError,
    analizarTarea,
    cargarResultado,
    limpiar,
  };
};

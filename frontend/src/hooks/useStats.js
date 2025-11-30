import { useEffect, useCallback } from 'react';

/**
 * Hook para gestionar estadísticas de la aplicación
 */
export function useStats() {
  // Obtener estadísticas actuales
  const getStats = useCallback(() => {
    const savedStats = localStorage.getItem('taskAnalyzerStats');
    if (savedStats) {
      return JSON.parse(savedStats);
    }
    return {
      totalTareas: 0,
      promedioPasos: 0,
      totalAmbiguedades: 0,
      totalPreguntas: 0,
      totalPasos: 0,
      ultimasActividades: []
    };
  }, []);

  // Actualizar estadísticas con nuevo resultado
  const updateStats = useCallback((resultado, tareaTexto) => {
    const currentStats = getStats();
    
    const numPasos = resultado.pasos?.length || 0;
    const numAmbiguedades = resultado.ambiguedades?.length || 0;
    const numPreguntas = resultado.preguntas?.length || 0;

    // Calcular nuevas estadísticas
    const newTotalTareas = currentStats.totalTareas + 1;
    const newTotalPasos = currentStats.totalPasos + numPasos;
    const newTotalAmbiguedades = currentStats.totalAmbiguedades + numAmbiguedades;
    const newTotalPreguntas = currentStats.totalPreguntas + numPreguntas;
    const newPromedioPasos = newTotalPasos / newTotalTareas;

    // Agregar a actividades recientes (máximo 5)
    const newActivity = {
      tarea: tareaTexto.substring(0, 50) + (tareaTexto.length > 50 ? '...' : ''),
      pasos: numPasos,
      ambiguedades: numAmbiguedades,
      preguntas: numPreguntas,
      fecha: new Date().toLocaleString('es-ES', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      })
    };

    const newActivities = [newActivity, ...currentStats.ultimasActividades].slice(0, 5);

    const newStats = {
      totalTareas: newTotalTareas,
      totalPasos: newTotalPasos,
      promedioPasos: newPromedioPasos,
      totalAmbiguedades: newTotalAmbiguedades,
      totalPreguntas: newTotalPreguntas,
      ultimasActividades: newActivities
    };

    // Guardar en localStorage
    localStorage.setItem('taskAnalyzerStats', JSON.stringify(newStats));

    // Emitir evento para actualizar UI
    window.dispatchEvent(new CustomEvent('statsUpdated', { detail: newStats }));

    return newStats;
  }, [getStats]);

  // Limpiar estadísticas
  const clearStats = useCallback(() => {
    const emptyStats = {
      totalTareas: 0,
      promedioPasos: 0,
      totalAmbiguedades: 0,
      totalPreguntas: 0,
      totalPasos: 0,
      ultimasActividades: []
    };
    localStorage.setItem('taskAnalyzerStats', JSON.stringify(emptyStats));
    window.dispatchEvent(new CustomEvent('statsUpdated', { detail: emptyStats }));
    return emptyStats;
  }, []);

  return {
    getStats,
    updateStats,
    clearStats
  };
}

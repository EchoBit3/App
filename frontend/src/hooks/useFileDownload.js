import { useCallback } from 'react';

/**
 * Hook para generar contenido de exportación
 */
export const useFileDownload = () => {
  /**
   * Genera el contenido formateado para descarga
   */
  const generateContent = useCallback((texto, resultado) => {
    const fecha = new Date().toLocaleDateString('es-ES');
    
    return `╔═══════════════════════════════════════════════════════════╗
║              DE-MYSTIFY - ANÁLISIS DE TAREA              ║
║                    Generado: ${fecha}                   ║
╚═══════════════════════════════════════════════════════════╝

📝 TAREA ORIGINAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${texto}

✅ CHECKLIST - PASOS CONCRETOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${resultado.pasos.map((paso, i) => `${i + 1}. ${paso}`).join('\n')}

⚠️  INFORMACIÓN FALTANTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${resultado.ambiguedades.length > 0 
  ? resultado.ambiguedades.map(amb => `• ${amb}`).join('\n')
  : '✨ ¡La tarea es suficientemente clara!'}

❓ PREGUNTAS SUGERIDAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${resultado.preguntas_sugeridas.length > 0
  ? resultado.preguntas_sugeridas.map(preg => `• ${preg}`).join('\n')
  : 'No hay preguntas adicionales'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ESTADÍSTICAS:
   • Pasos identificados: ${resultado.pasos.length}
   • Ambigüedades detectadas: ${resultado.ambiguedades.length}
   • Preguntas sugeridas: ${resultado.preguntas_sugeridas.length}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Generado por De-Mystify
   Desglosador de Tareas con IA
   https://github.com/tu-repo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
  }, []);

  /**
   * Descarga el resultado como archivo TXT
   */
  const descargarResultado = useCallback((texto, resultado) => {
    if (!resultado) {
      return;
    }

    const contenido = generateContent(texto, resultado);
    const blob = new Blob([contenido], { type: 'text/plain; charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `demystify_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [generateContent]);

  return { descargarResultado };
};

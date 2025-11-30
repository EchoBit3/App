import { useCallback } from 'react';
import toast from 'react-hot-toast';

/**
 * Hook para compartir resultados
 */
export const useShare = () => {
  /**
   * Genera el texto para compartir
   */
  const generateShareText = useCallback((resultado) => {
    return `🎯 De-Mystify - Análisis de Tarea\n\n✅ ${resultado.pasos.length} pasos identificados\n⚠️ ${resultado.ambiguedades.length} ambigüedades detectadas\n\n¡Prueba De-Mystify para desglosar tus tareas!`;
  }, []);

  /**
   * Comparte el resultado usando la API nativa o clipboard
   */
  const compartirResultado = useCallback(async (resultado) => {
    if (!resultado) {
      return;
    }

    const textoCompartir = generateShareText(resultado);

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'De-Mystify - Análisis de Tarea',
          text: textoCompartir,
        });
        toast.success('¡Compartido exitosamente!');
      } catch (err) {
        // Si el usuario cancela, no hacer nada
        if (err.name !== 'AbortError') {
          // Intentar copiar al portapapeles como fallback
          try {
            await navigator.clipboard.writeText(textoCompartir);
            toast.success('¡Texto copiado al portapapeles!');
          } catch (clipboardErr) {
            toast.error('No se pudo compartir. Intenta copiar manualmente.');
          }
        }
      }
    } else {
      // Navegadores sin API de compartir
      try {
        await navigator.clipboard.writeText(textoCompartir);
        toast.success('¡Texto copiado al portapapeles!');
      } catch (err) {
        // Fallback final: crear elemento temporal para copiar
        const textArea = document.createElement('textarea');
        textArea.value = textoCompartir;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
          document.execCommand('copy');
          toast.success('¡Texto copiado!');
        } catch (copyErr) {
          toast.error('No se pudo copiar el texto automáticamente', {
            duration: 5000,
          });
        } finally {
          document.body.removeChild(textArea);
        }
      }
    }
  }, [generateShareText]);

  return { compartirResultado };
};

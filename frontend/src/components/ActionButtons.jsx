import { motion } from 'framer-motion';
import { Download, Share2 } from 'lucide-react';
import { ANIMATION_DELAYS } from '../constants/ui';

/**
 * Botones de acción para descargar y compartir resultados
 */
export default function ActionButtons({ onDescargar, onCompartir }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: ANIMATION_DELAYS.BUTTONS }}
      className="mt-6 flex flex-wrap gap-4 justify-center"
    >
      <motion.button
        whileHover={{ scale: 1.05, y: -2 }}
        whileTap={{ scale: 0.95 }}
        onClick={onDescargar}
        className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
        aria-label="Descargar resultado"
      >
        <Download className="w-5 h-5" />
        Descargar como TXT
      </motion.button>

      <motion.button
        whileHover={{ scale: 1.05, y: -2 }}
        whileTap={{ scale: 0.95 }}
        onClick={onCompartir}
        className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
        aria-label="Compartir resultado"
      >
        <Share2 className="w-5 h-5" />
        Compartir
      </motion.button>
    </motion.div>
  );
}

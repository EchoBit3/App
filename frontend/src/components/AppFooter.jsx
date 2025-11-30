import { motion } from 'framer-motion';
import { Heart } from 'lucide-react';
import { ANIMATION_DELAYS } from '../constants/ui';

/**
 * Footer de la aplicación
 */
export default function AppFooter() {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: ANIMATION_DELAYS.FOOTER }}
      className="mt-12 mb-6 text-center"
    >
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
        <p className="text-white/90 text-sm flex items-center justify-center gap-2 flex-wrap">
          <span>Desarrollado con</span>
          <Heart className="w-4 h-4 text-red-400 animate-pulse fill-red-400" />
          <span>usando React + FastAPI + Google Gemini</span>
        </p>
        <p className="mt-2 text-white/80 text-xs">
          🆓 Completamente GRATIS y Open Source
        </p>
        <div className="mt-3 flex justify-center gap-4 text-white/70 text-xs">
          <a href="#" className="hover:text-white transition-colors">Documentación</a>
          <span>•</span>
          <a href="#" className="hover:text-white transition-colors">GitHub</a>
          <span>•</span>
          <a href="#" className="hover:text-white transition-colors">Reportar Bug</a>
        </div>
      </div>
    </motion.footer>
  );
}

import { motion } from 'framer-motion';
import { Menu, X, Github, Sparkles } from 'lucide-react';

export default function Header({ showSidebar, setShowSidebar }) {
  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="bg-white/10 backdrop-blur-md border-b border-white/20 sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo y Título */}
          <motion.div 
            className="flex items-center gap-3"
            whileHover={{ scale: 1.02 }}
          >
            <motion.span 
              className="text-4xl"
              animate={{ rotate: [0, 10, -10, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            >
              🎯
            </motion.span>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                De-Mystify
                <Sparkles className="w-5 h-5 text-yellow-300" />
              </h1>
              <p className="text-white/80 text-sm">El Desglosador de Tareas con IA</p>
            </div>
          </motion.div>

          {/* Botones de navegación */}
          <div className="flex items-center gap-3">
            {/* GitHub Link */}
            <motion.a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.1, rotate: 5 }}
              whileTap={{ scale: 0.9 }}
              className="hidden sm:flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-white transition-all"
            >
              <Github className="w-5 h-5" />
              <span className="hidden md:inline">GitHub</span>
            </motion.a>

            {/* Toggle Sidebar (Mobile) */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowSidebar(!showSidebar)}
              className="md:hidden p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-all"
            >
              {showSidebar ? (
                <X className="w-6 h-6 text-white" />
              ) : (
                <Menu className="w-6 h-6 text-white" />
              )}
            </motion.button>
          </div>
        </div>

        {/* Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-3 flex flex-wrap gap-4 text-white/90 text-sm"
        >
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            <span>API Activa</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🆓</span>
            <span>100% Gratis</span>
          </div>
          <div className="flex items-center gap-2">
            <span>⚡</span>
            <span>Google Gemini AI</span>
          </div>
        </motion.div>
      </div>
    </motion.header>
  );
}

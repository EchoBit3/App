import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

export default function ExampleCard({ ejemplo, onClick }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="w-full p-4 bg-slate-200/90 backdrop-blur-sm rounded-xl border-2 border-slate-300/50 hover:border-indigo-400 hover:shadow-lg hover:bg-slate-200 transition-all text-left group"
    >
      <div className="flex items-start gap-3">
        <motion.span 
          className="text-2xl flex-shrink-0"
          whileHover={{ rotate: [0, -10, 10, 0] }}
          transition={{ duration: 0.3 }}
        >
          {ejemplo.categoria.split(' ')[0]}
        </motion.span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <h4 className="font-semibold text-gray-800 group-hover:text-purple-600 transition-colors text-sm">
              {ejemplo.categoria.substring(ejemplo.categoria.indexOf(' ') + 1)}
            </h4>
            <ArrowRight className="w-4 h-4 text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
          </div>
          <p className="text-xs text-gray-600 line-clamp-2 leading-relaxed">
            {ejemplo.texto}
          </p>
        </div>
      </div>
    </motion.button>
  );
}

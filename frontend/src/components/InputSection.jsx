import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Loader2, AlertCircle, RotateCcw, Zap } from 'lucide-react';

export default function InputSection({ 
  texto, 
  setTexto, 
  loading, 
  error, 
  setError, 
  handleAnalizar,
  setResultado 
}) {
  const handleClear = () => {
    setTexto('');
    setError('');
    setResultado(null);
  };

  const caracteresRestantes = 2000 - texto.length;
  const progreso = (texto.length / 2000) * 100;
  const esValido = texto.trim().length >= 10 && texto.length <= 2000;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-200/90 backdrop-blur-md rounded-2xl shadow-xl p-6 md:p-8 flex flex-col"
    >
      {/* Input Area */}
      <div className="mb-4 flex-shrink-0">
        <label className="block text-gray-800 font-semibold mb-3 text-lg flex items-center gap-2">
          <span className="text-2xl">📝</span>
          Pega aquí tu tarea o instrucción ambigua:
        </label>
        
        <div className="relative">
          <textarea
            value={texto}
            onChange={(e) => {
              setTexto(e.target.value);
              setError('');
            }}
            placeholder='Ejemplo: "Hacer un análisis del mercado para el viernes"

Pega aquí cualquier instrucción vaga de tu profesor, jefe o cliente...'
            className="w-full h-28 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all resize-none text-gray-700 placeholder:text-gray-400"
            disabled={loading}
          />
          
          {/* Clear Button */}
          {texto && !loading && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              whileHover={{ scale: 1.1, rotate: 180 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleClear}
              className="absolute top-3 right-3 p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              title="Limpiar texto"
            >
              <RotateCcw className="w-4 h-4 text-gray-600" />
            </motion.button>
          )}
        </div>

        {/* Character Counter & Progress Bar */}
        <div className="mt-2 space-y-1 flex-shrink-0">
          {/* Progress Bar */}
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progreso}%` }}
              className={`h-full transition-colors ${
                texto.length > 2000 
                  ? 'bg-red-500' 
                  : texto.length >= 10 
                  ? 'bg-gradient-to-r from-indigo-500 to-blue-500' 
                  : 'bg-gray-300'
              }`}
            />
          </div>

          {/* Stats Row */}
          <div className="flex justify-between items-center text-sm">
            <div className="flex items-center gap-4">
              <span className={`font-medium ${
                texto.length > 2000 ? 'text-red-600' : 'text-gray-600'
              }`}>
                {texto.length} / 2000 caracteres
              </span>
              
              {texto.length > 0 && texto.length < 10 && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-amber-600 flex items-center gap-1"
                >
                  <AlertCircle className="w-4 h-4" />
                  Mínimo 10 caracteres
                </motion.span>
              )}
              
              {esValido && (
                <motion.span
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-green-600 flex items-center gap-1 font-medium"
                >
                  <Zap className="w-4 h-4" />
                  ¡Listo para analizar!
                </motion.span>
              )}
            </div>

            <span className={`${
              caracteresRestantes < 100 ? 'text-amber-600' : 'text-gray-500'
            }`}>
              {caracteresRestantes} restantes
            </span>
          </div>
        </div>
      </div>

      {/* Spacer para centrar el botón */}
      <div className="flex-grow"></div>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -10, height: 0 }}
            className="mb-2 overflow-hidden flex-shrink-0"
          >
            <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-red-700 font-medium">Error de validación</p>
                <p className="text-red-600 text-sm mt-1">{error}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Action Button */}
      <motion.button
        whileHover={{ scale: esValido && !loading ? 1.02 : 1 }}
        whileTap={{ scale: esValido && !loading ? 0.98 : 1 }}
        onClick={handleAnalizar}
        disabled={loading || !esValido}
        className={`w-full py-3 font-semibold rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 flex-shrink-0 ${
          loading || !esValido
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-60'
            : 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white hover:shadow-xl hover:from-indigo-700 hover:to-blue-700'
        }`}
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="animate-pulse">Analizando tu tarea con IA...</span>
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            <span>🪄 Desambiguar (Traducir a Humano)</span>
          </>
        )}
      </motion.button>

      {/* Quick Tips */}
      {!texto && !loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-100"
        >
          <p className="text-sm text-blue-800 font-medium mb-2">💡 Consejo:</p>
          <p className="text-sm text-blue-700">
            Cuanta más información proporciones en tu instrucción, mejor será el análisis.
            Incluye fechas, objetivos, formato deseado, etc.
          </p>
        </motion.div>
      )}
    </motion.div>
  );
}

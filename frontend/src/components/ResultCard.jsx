import { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, AlertTriangle, HelpCircle, Check, Copy, Sparkles } from 'lucide-react';

export default function ResultCard({ pasos, ambiguedades, preguntas }) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-8"
    >
      {/* Success Message */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-xl"
      >
        <div className="flex items-center gap-3">
          <Sparkles className="w-6 h-6 text-green-500" />
          <div>
            <p className="text-green-800 font-semibold">¡Análisis completado exitosamente!</p>
            <p className="text-green-600 text-sm">Tu tarea ha sido desglosada en pasos accionables</p>
          </div>
        </div>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Columna Izquierda: Checklist */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-slate-200/90 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-slate-300/50"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle2 className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-800">
                Lista de Tareas
              </h3>
              <p className="text-sm text-gray-500">Pasos concretos y accionables</p>
            </div>
          </div>
          
          {pasos.length > 0 ? (
            <div className="space-y-3">
              {pasos.map((paso, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="group relative"
                >
                  <div className="flex gap-3 p-4 bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 rounded-xl border border-green-200 hover:shadow-lg hover:border-green-300 transition-all">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-lg">
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-800 text-sm font-medium leading-relaxed">{paso}</p>
                    </div>
                    <button
                      onClick={() => copyToClipboard(paso, `paso-${index}`)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white rounded-lg"
                      title="Copiar paso"
                    >
                      {copiedIndex === `paso-${index}` ? (
                        <Check className="w-4 h-4 text-green-600" />
                      ) : (
                        <Copy className="w-4 h-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-gray-400 italic">No se generaron pasos específicos.</p>
            </div>
          )}

          {pasos.length > 0 && (
            <div className="mt-4 p-3 bg-gradient-to-r from-green-100 to-emerald-100 rounded-lg">
              <p className="text-sm text-green-800 font-medium text-center">
                ✨ Total: {pasos.length} {pasos.length === 1 ? 'paso' : 'pasos'} identificados
              </p>
            </div>
          )}
        </motion.div>

        {/* Columna Derecha: Ambigüedades y Preguntas */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          {/* Ambigüedades */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-gray-100/50">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-amber-100 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-amber-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800">
                  Detector de Ambigüedad
                </h3>
                <p className="text-sm text-gray-500">Información faltante o poco clara</p>
              </div>
            </div>
            
            {ambiguedades.length > 0 ? (
              <div className="space-y-3">
                {ambiguedades.map((amb, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="p-4 bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 rounded-xl border border-amber-200 hover:shadow-lg hover:border-amber-300 transition-all"
                  >
                    <p className="text-gray-800 text-sm font-medium">{amb}</p>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border-2 border-green-200 text-center">
                <Sparkles className="w-8 h-8 text-green-500 mx-auto mb-2" />
                <p className="text-green-700 font-semibold">¡La tarea es suficientemente clara!</p>
                <p className="text-green-600 text-sm mt-1">No se detectaron ambigüedades</p>
              </div>
            )}
          </div>

          {/* Preguntas Sugeridas */}
          {preguntas.length > 0 && (
            <div className="bg-slate-200/90 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-slate-300/50">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <HelpCircle className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="text-lg font-bold text-gray-800">
                    Preguntas que deberías hacer
                  </h4>
                  <p className="text-sm text-gray-500">Para clarificar la tarea</p>
                </div>
              </div>
              <div className="space-y-3">
                {preguntas.map((preg, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * index + 0.3 }}
                    className="group relative"
                  >
                    <div className="flex items-start gap-3 p-4 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-xl border border-blue-200 hover:shadow-lg hover:border-blue-300 transition-all">
                      <span className="text-blue-500 font-bold text-lg">•</span>
                      <p className="text-gray-800 text-sm font-medium flex-1">{preg}</p>
                      <button
                        onClick={() => copyToClipboard(preg, `pregunta-${index}`)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-white rounded-lg"
                        title="Copiar pregunta"
                      >
                        {copiedIndex === `pregunta-${index}` ? (
                          <Check className="w-4 h-4 text-blue-600" />
                        ) : (
                          <Copy className="w-4 h-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}

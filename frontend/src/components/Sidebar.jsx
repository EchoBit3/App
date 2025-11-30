import { motion, AnimatePresence } from 'framer-motion';
import { Lightbulb, Target, AlertTriangle, List, HelpCircle } from 'lucide-react';
import ExampleCard from './ExampleCard';

export default function Sidebar({ showSidebar, ejemplos, handleEjemplo }) {
  return (
    <AnimatePresence>
      {showSidebar && (
        <>
          {/* Sidebar */}
          <motion.aside
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            className="fixed md:relative md:block w-80 flex-shrink-0 z-50 md:z-auto"
          >
            <div className="h-screen md:h-auto overflow-y-auto">
              <div className="bg-slate-200/90 backdrop-blur-md rounded-none md:rounded-2xl shadow-xl p-6 m-0">
                {/* Header */}
                <div className="flex items-center gap-2 mb-4">
                  <Target className="w-6 h-6 text-purple-600" />
                  <h2 className="text-xl font-bold text-gray-800">
                    Acerca de De-Mystify
                  </h2>
                </div>

                {/* Descripción */}
                <p className="text-gray-600 text-sm mb-4">
                  <strong>De-Mystify</strong> utiliza Inteligencia Artificial para transformar
                  instrucciones vagas en planes accionables:
                </p>

                {/* Características */}
                <div className="space-y-3 mb-6">
                  <FeatureItem
                    icon={<List className="w-5 h-5 text-green-500" />}
                    title="Desglosar tareas complejas"
                    description="en pasos simples y accionables"
                  />
                  <FeatureItem
                    icon={<AlertTriangle className="w-5 h-5 text-amber-500" />}
                    title="Identificar información faltante"
                    description="que te bloquea o genera dudas"
                  />
                  <FeatureItem
                    icon={<Target className="w-5 h-5 text-blue-500" />}
                    title="Generar checklists"
                    description="para empezar de inmediato"
                  />
                  <FeatureItem
                    icon={<HelpCircle className="w-5 h-5 text-purple-500" />}
                    title="Sugerir preguntas clave"
                    description="para aclarar ambigüedades"
                  />
                </div>

                {/* ¿Cuándo usarlo? */}
                <div className="border-t border-gray-200 pt-4 mb-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Lightbulb className="w-5 h-5 text-yellow-500" />
                    <h3 className="font-semibold text-gray-800">
                      ¿Cuándo usarlo?
                    </h3>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600">
                    <UseCaseItem emoji="🎓" text="Instrucciones vagas de profesores" />
                    <UseCaseItem emoji="💼" text="Tareas ambiguas del trabajo" />
                    <UseCaseItem emoji="🎯" text="Proyectos sin claridad" />
                    <UseCaseItem emoji="📝" text="Evaluaciones confusas" />
                    <UseCaseItem emoji="🚀" text="Objetivos poco definidos" />
                  </div>
                </div>

                {/* Ejemplos */}
                {ejemplos.length > 0 && (
                  <div className="border-t border-gray-200 pt-4">
                    <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <span className="text-xl">📌</span>
                      Prueba con un ejemplo:
                    </h3>
                    <div className="space-y-2 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
                      {ejemplos.map((ejemplo, index) => (
                        <ExampleCard
                          key={index}
                          ejemplo={ejemplo}
                          onClick={() => handleEjemplo(ejemplo.texto)}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Footer Stats */}
                <div className="border-t border-gray-200 pt-4 mt-4">
                  <div className="grid grid-cols-2 gap-3 text-center">
                    <div className="bg-purple-50 rounded-lg p-3">
                      <div className="text-2xl font-bold text-purple-600">100%</div>
                      <div className="text-xs text-gray-600">Gratis</div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3">
                      <div className="text-2xl font-bold text-blue-600">AI</div>
                      <div className="text-xs text-gray-600">Gemini 2.5</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}

function FeatureItem({ icon, title, description }) {
  return (
    <motion.div
      whileHover={{ x: 4 }}
      className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
    >
      <div className="flex-shrink-0 mt-0.5">{icon}</div>
      <div>
        <div className="font-semibold text-gray-800 text-sm">{title}</div>
        <div className="text-xs text-gray-600">{description}</div>
      </div>
    </motion.div>
  );
}

function UseCaseItem({ emoji, text }) {
  return (
    <motion.div
      whileHover={{ x: 4 }}
      className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 transition-colors"
    >
      <span className="text-lg">{emoji}</span>
      <span>{text}</span>
    </motion.div>
  );
}

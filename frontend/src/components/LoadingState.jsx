import { motion } from 'framer-motion';
import { Brain, Sparkles, Zap, Target } from 'lucide-react';

export default function LoadingState() {
  const steps = [
    { icon: Brain, text: 'Procesando con IA...', delay: 0 },
    { icon: Sparkles, text: 'Analizando ambigüedades...', delay: 0.3 },
    { icon: Zap, text: 'Generando pasos...', delay: 0.6 },
    { icon: Target, text: 'Creando preguntas...', delay: 0.9 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mt-8 bg-slate-200/90 backdrop-blur-md rounded-2xl shadow-xl p-8"
    >
      <div className="max-w-md mx-auto">
        {/* Animated Brain Icon */}
        <motion.div
          className="flex justify-center mb-6"
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 5, -5, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <div className="relative">
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full blur-2xl opacity-50"
              animate={{ scale: [1, 1.5, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <Brain className="w-20 h-20 text-purple-600 relative z-10" />
          </div>
        </motion.div>

        {/* Progress Steps */}
        <div className="space-y-4">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: step.delay }}
              className="flex items-center gap-3"
            >
              <motion.div
                animate={{ 
                  scale: [1, 1.2, 1],
                  rotate: [0, 180, 360]
                }}
                transition={{ 
                  duration: 1.5,
                  repeat: Infinity,
                  delay: step.delay
                }}
                className="p-2 bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg"
              >
                <step.icon className="w-5 h-5 text-purple-600" />
              </motion.div>
              
              <div className="flex-1">
                <p className="text-gray-700 font-medium">{step.text}</p>
                <div className="mt-1 h-1 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: '0%' }}
                    animate={{ width: '100%' }}
                    transition={{ 
                      duration: 1.5, 
                      delay: step.delay,
                      repeat: Infinity,
                      repeatDelay: 0.5
                    }}
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                  />
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Fun Facts */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-6 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl"
        >
          <p className="text-sm text-gray-600 text-center">
            <span className="font-semibold">💡 Sabías que:</span> La IA está procesando
            tu tarea usando Google Gemini 2.5, uno de los modelos más avanzados del mundo.
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}

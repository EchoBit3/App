import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ChartBarIcon, 
  ClockIcon, 
  CheckCircleIcon,
  QuestionMarkCircleIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  LightBulbIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

/**
 * Dashboard con estadísticas en tiempo real
 */
export default function Dashboard({ onStatsUpdate }) {
  const [stats, setStats] = useState({
    totalTareas: 0,
    promedioPasos: 0,
    totalAmbiguedades: 0,
    totalPreguntas: 0,
    ultimasActividades: []
  });

  // Cargar estadísticas del localStorage al montar
  useEffect(() => {
    const savedStats = localStorage.getItem('taskAnalyzerStats');
    if (savedStats) {
      setStats(JSON.parse(savedStats));
    }

    // Escuchar actualizaciones de estadísticas
    const handleStatsUpdate = (event) => {
      setStats(event.detail);
    };

    window.addEventListener('statsUpdated', handleStatsUpdate);
    return () => window.removeEventListener('statsUpdated', handleStatsUpdate);
  }, []);

  // Notificar cambios al padre
  useEffect(() => {
    if (onStatsUpdate) {
      onStatsUpdate(stats);
    }
  }, [stats, onStatsUpdate]);

  const StatCard = ({ icon: Icon, title, value, subtitle, color = "indigo" }) => {
    const colorClasses = {
      indigo: 'text-indigo-400 bg-indigo-500/10',
      green: 'text-green-400 bg-green-500/10',
      yellow: 'text-yellow-400 bg-yellow-500/10',
      blue: 'text-blue-400 bg-blue-500/10'
    };
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-700/50 backdrop-blur-sm rounded-xl p-4 border border-slate-600/50 hover:border-slate-500/50 transition-all"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-slate-400 text-xs font-medium mb-1">{title}</p>
            <p className={`text-2xl font-bold ${colorClasses[color].split(' ')[0]} mb-0.5`}>{value}</p>
            {subtitle && <p className="text-slate-500 text-xs">{subtitle}</p>}
          </div>
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
      </motion.div>
    );
  };

  const ActivityItem = ({ activity, index }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="flex items-start space-x-3 p-3 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-all"
    >
      <div className="flex-shrink-0 mt-1">
        <div className="w-2 h-2 bg-indigo-400 rounded-full"></div>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-slate-300 text-sm truncate">{activity.tarea}</p>
        <p className="text-slate-500 text-xs mt-1">
          {activity.pasos} pasos • {activity.ambiguedades} ambigüedades • {activity.preguntas} preguntas
        </p>
        <p className="text-slate-600 text-xs mt-1">{activity.fecha}</p>
      </div>
    </motion.div>
  );

  return (
    <div className="space-y-6 mt-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-2xl font-bold text-white mb-1">
          Panel de Estadísticas
        </h2>
        <p className="text-slate-400 text-sm">
          Monitoreo en tiempo real de tu actividad
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard
          icon={ChartBarIcon}
          title="Tareas Analizadas"
          value={stats.totalTareas}
          subtitle="Total acumulado"
          color="indigo"
        />
        <StatCard
          icon={CheckCircleIcon}
          title="Promedio de Pasos"
          value={stats.promedioPasos.toFixed(1)}
          subtitle="Por tarea"
          color="green"
        />
        <StatCard
          icon={ExclamationTriangleIcon}
          title="Ambigüedades"
          value={stats.totalAmbiguedades}
          subtitle="Total detectadas"
          color="yellow"
        />
        <StatCard
          icon={QuestionMarkCircleIcon}
          title="Preguntas"
          value={stats.totalPreguntas}
          subtitle="Total generadas"
          color="blue"
        />
      </div>

      {/* Actividad Reciente */}
      {stats.ultimasActividades.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-slate-700/30 backdrop-blur-sm rounded-xl p-6 border border-slate-600/50"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <ClockIcon className="w-5 h-5 text-indigo-400" />
              <h3 className="text-lg font-semibold text-white">Actividad Reciente</h3>
            </div>
            <span className="text-sm text-slate-500">
              Últimas {stats.ultimasActividades.length} tareas
            </span>
          </div>
          <div className="space-y-2">
            {stats.ultimasActividades.map((activity, index) => (
              <ActivityItem key={index} activity={activity} index={index} />
            ))}
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {stats.totalTareas === 0 && (
        <>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
            className="text-center py-6"
          >
            <ArrowTrendingUpIcon className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-slate-400 mb-1">
              Aún no hay datos
            </h3>
            <p className="text-slate-500 text-sm">
              Las estadísticas aparecerán cuando analices tu primera tarea
            </p>
          </motion.div>

          {/* Consejos y Guía de Uso */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {/* Cómo funciona */}
            <div className="bg-slate-700/30 backdrop-blur-sm rounded-xl p-5 border border-slate-600/50">
              <div className="flex items-center gap-2 mb-3">
                <SparklesIcon className="w-5 h-5 text-purple-400" />
                <h4 className="text-white font-semibold">¿Cómo funciona?</h4>
              </div>
              <ul className="space-y-2 text-slate-300 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-0.5">1.</span>
                  <span>Pega una instrucción vaga o ambigua</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-0.5">2.</span>
                  <span>La IA la analiza y desglosa en pasos</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-0.5">3.</span>
                  <span>Identifica ambigüedades e información faltante</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-0.5">4.</span>
                  <span>Genera preguntas para aclarar dudas</span>
                </li>
              </ul>
            </div>

            {/* Consejos */}
            <div className="bg-slate-700/30 backdrop-blur-sm rounded-xl p-5 border border-slate-600/50">
              <div className="flex items-center gap-2 mb-3">
                <LightBulbIcon className="w-5 h-5 text-yellow-400" />
                <h4 className="text-white font-semibold">Consejos Pro</h4>
              </div>
              <ul className="space-y-2 text-slate-300 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">💡</span>
                  <span>Incluye contexto: fechas, personas involucradas, objetivos</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">💡</span>
                  <span>Menciona el formato deseado del resultado final</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">💡</span>
                  <span>Entre más detalles, más preciso será el análisis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">💡</span>
                  <span>Revisa el historial para reutilizar análisis anteriores</span>
                </li>
              </ul>
            </div>
          </motion.div>

          {/* Ejemplos rápidos */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="bg-gradient-to-r from-indigo-500/10 to-blue-500/10 backdrop-blur-sm rounded-xl p-5 border border-indigo-500/30"
          >
            <div className="flex items-center gap-2 mb-3">
              <SparklesIcon className="w-5 h-5 text-indigo-400" />
              <h4 className="text-white font-semibold">Ejemplos de Instrucciones</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50">
                <p className="text-slate-300 italic">"Hacer un informe de ventas para el lunes"</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50">
                <p className="text-slate-300 italic">"Preparar presentación del proyecto"</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50">
                <p className="text-slate-300 italic">"Analizar competencia del mercado"</p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </div>
  );
}

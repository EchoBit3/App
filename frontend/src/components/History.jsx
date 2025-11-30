import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  ClockIcon, 
  TrashIcon, 
  MagnifyingGlassIcon,
  ChevronLeftIcon,
  ChevronRightIcon 
} from '@heroicons/react/24/outline';
import ConfirmDialog from './ConfirmDialog';

export default function History({ onSelectQuery }) {
  const { token } = useAuth();
  const [historial, setHistorial] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const limit = 10;

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

  useEffect(() => {
    if (token) {
      loadHistory();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, page]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const offset = page * limit;
      const response = await axios.get(
        `${API_URL}/api/historial?limit=${limit}&offset=${offset}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      setHistorial(response.data.historial);
      setTotal(response.data.total);
      setError('');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al cargar el historial';
      setError(errorMsg);
      console.error('Error al cargar historial:', err);
      setHistorial([]);
    } finally {
      setLoading(false);
    }
  };

  const deleteQuery = async (id) => {
    setConfirmDelete(id);
  };

  const handleConfirmDelete = async () => {
    const id = confirmDelete;
    setConfirmDelete(null);

    try {
      await axios.delete(`${API_URL}/api/historial/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Actualizar estado local
      setHistorial(prev => prev.filter(h => h.id !== id));
      setTotal(prev => prev - 1);
      
      // Si la página quedó vacía y no es la primera, retroceder
      if (historial.length === 1 && page > 0) {
        setPage(prev => prev - 1);
      }
      
      toast.success('Consulta eliminada exitosamente');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al eliminar la consulta';
      console.error('Error al eliminar:', err);
      toast.error(errorMsg);
      // Recargar en caso de error para sincronizar
      await loadHistory();
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      // Verificar que la fecha sea válida
      if (isNaN(date.getTime())) {
        return 'Fecha inválida';
      }
      return new Intl.DateTimeFormat('es', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (error) {
      console.error('Error formateando fecha:', error);
      return dateString; // Fallback: mostrar string original
    }
  };

  const truncateText = (text, maxLength = 60) => {
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength) + '...';
  };

  const totalPages = Math.ceil(total / limit);

  if (loading && historial.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-slate-200/90 backdrop-blur-sm dark:bg-gray-800 rounded-xl shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <ClockIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Historial
          </h2>
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {total} consulta{total !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && historial.length === 0 && (
        <div className="text-center py-12">
          <MagnifyingGlassIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            No hay consultas en tu historial
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
            Comienza analizando una tarea para ver tu historial
          </p>
        </div>
      )}

      {/* History list */}
      <div className="space-y-3">
        {historial.map((consulta) => (
          <div
            key={consulta.id}
            className="group relative p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 transition-all cursor-pointer"
            onClick={() => onSelectQuery(consulta)}
          >
            {/* Query text */}
            <p className="text-gray-900 dark:text-white font-medium mb-2">
              {truncateText(consulta.texto_original)}
            </p>

            {/* Metadata */}
            <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
              <div className="flex items-center space-x-4">
                <span className="flex items-center space-x-1">
                  <ClockIcon className="w-4 h-4" />
                  <span>{formatDate(consulta.created_at)}</span>
                </span>
                {consulta.cached && (
                  <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                    Cache
                  </span>
                )}
                <span className="text-gray-500">
                  {consulta.tiempo_respuesta_ms}ms
                </span>
              </div>

              {/* Delete button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteQuery(consulta.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                title="Eliminar"
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>

            {/* Stats */}
            <div className="mt-3 flex items-center space-x-3 text-xs">
              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">
                {consulta.pasos?.length || 0} pasos
              </span>
              <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded">
                {consulta.ambiguedades?.length || 0} ambigüedades
              </span>
              <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded">
                {consulta.preguntas?.length || 0} preguntas
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0 || loading}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <ChevronLeftIcon className="w-4 h-4" />
            <span>Anterior</span>
          </button>

          <span className="text-sm text-gray-600 dark:text-gray-400">
            Página {page + 1} de {totalPages}
          </span>

          <button
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1 || loading}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <span>Siguiente</span>
            <ChevronRightIcon className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={confirmDelete !== null}
        title="Eliminar consulta"
        message="¿Estás seguro de eliminar esta consulta del historial? Esta acción no se puede deshacer."
        onConfirm={handleConfirmDelete}
        onCancel={() => setConfirmDelete(null)}
      />
    </div>
  );
}

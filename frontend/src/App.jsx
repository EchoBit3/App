import { useState, useEffect, useCallback } from 'react';
import { api } from './services/api';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { useTaskAnalyzer } from './hooks/useTaskAnalyzer';
import { useFileDownload } from './hooks/useFileDownload';
import { useShare } from './hooks/useShare';
import { useStats } from './hooks/useStats';
import { RESPONSIVE_BREAKPOINTS } from './constants/ui';
import { Toaster } from 'react-hot-toast';

// Components
import AuthHeader from './components/AuthHeader';
import AuthModals from './components/AuthModals';
import Sidebar from './components/Sidebar';
import InputSection from './components/InputSection';
import ResultCard from './components/ResultCard';
import LoadingState from './components/LoadingState';
import ActionButtons from './components/ActionButtons';
import AppFooter from './components/AppFooter';
import Dashboard from './components/Dashboard';

/**
 * Componente principal de la aplicación
 */
function AppContent() {
  const { user, logout, isAuthenticated, loading: authLoading } = useAuth();
  const { loading, error, resultado, setError, analizarTarea, cargarResultado, limpiar } = useTaskAnalyzer();
  const { descargarResultado } = useFileDownload();
  const { compartirResultado } = useShare();
  const { updateStats } = useStats();

  // UI State
  const [texto, setTexto] = useState('');
  const [ejemplos, setEjemplos] = useState([]);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [showHistory, setShowHistory] = useState(false);

  // Cargar ejemplos al montar
  useEffect(() => {
    let mounted = true;

    api.obtenerEjemplos()
      .then(data => {
        if (mounted) {
          setEjemplos(data);
        }
      })
      .catch(err => {
        if (mounted) {
          console.error('Error cargando ejemplos:', err);
          setEjemplos([]); // Establecer array vacío en caso de error
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  /**
   * Handler para analizar tarea
   */
  const handleAnalizar = useCallback(async () => {
    const result = await analizarTarea(texto, isAuthenticated);
    
    if (result.requiresAuth) {
      setShowAuth(true);
      setAuthMode('login');
    } else if (result && !result.requiresAuth) {
      // Actualizar estadísticas en tiempo real
      updateStats(result, texto);
    }
  }, [texto, isAuthenticated, analizarTarea, updateStats]);

  /**
   * Handler para seleccionar consulta del historial
   */
  const handleSelectQuery = useCallback((consulta) => {
    setTexto(consulta.texto_original);
    cargarResultado(consulta);
    setShowHistory(false);
  }, [cargarResultado]);

  /**
   * Handler para autenticación exitosa
   */
  const handleAuthSuccess = useCallback(() => {
    setShowAuth(false);
    setError('');
  }, [setError]);

  /**
   * Handler para seleccionar ejemplo
   */
  const handleEjemplo = useCallback((ejemploTexto) => {
    setTexto(ejemploTexto);
    limpiar();
    
    // Scroll al input en móvil
    if (window.innerWidth < RESPONSIVE_BREAKPOINTS.MOBILE) {
      setShowSidebar(false);
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }, 100);
    }
  }, [limpiar]);

  /**
   * Handlers para modales
   */
  const handleShowAuth = useCallback(() => {
    setShowAuth(true);
    setAuthMode('login');
  }, []);

  const handleShowHistory = useCallback(() => {
    setShowHistory(prev => !prev);
  }, []);

  // Loading state durante autenticación
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-700 via-gray-800 to-slate-800 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-400" aria-label="Cargando..."></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-700 via-gray-800 to-slate-800">
      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />

      {/* Header */}
      <AuthHeader
        isAuthenticated={isAuthenticated}
        user={user}
        showSidebar={showSidebar}
        setShowSidebar={setShowSidebar}
        onShowHistory={handleShowHistory}
        onShowAuth={handleShowAuth}
        onLogout={logout}
      />

      {/* Modales */}
      <AuthModals
        showAuth={showAuth}
        showHistory={showHistory}
        authMode={authMode}
        isAuthenticated={isAuthenticated}
        onCloseAuth={() => setShowAuth(false)}
        onCloseHistory={() => setShowHistory(false)}
        onSwitchAuthMode={setAuthMode}
        onAuthSuccess={handleAuthSuccess}
        onSelectQuery={handleSelectQuery}
      />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 flex gap-6">
        {/* Sidebar */}
        <Sidebar 
          showSidebar={showSidebar}
          ejemplos={ejemplos}
          handleEjemplo={handleEjemplo}
        />

        {/* Main Section */}
        <main className="flex-1 min-w-0">
          {/* Input */}
          <InputSection
            texto={texto}
            setTexto={setTexto}
            loading={loading}
            error={error}
            setError={setError}
            handleAnalizar={handleAnalizar}
            setResultado={limpiar}
          />

          {/* Loading */}
          {loading && <LoadingState />}

          {/* Dashboard - Solo cuando no hay resultado ni loading */}
          {!resultado && !loading && (
            <Dashboard />
          )}

          {/* Results */}
          {resultado && !loading && (
            <div id="resultados">
              <ResultCard
                pasos={resultado.pasos}
                ambiguedades={resultado.ambiguedades}
                preguntas={resultado.preguntas_sugeridas}
              />

              <ActionButtons
                onDescargar={() => descargarResultado(texto, resultado)}
                onCompartir={() => compartirResultado(resultado)}
              />
            </div>
          )}

          {/* Footer */}
          <AppFooter />
        </main>
      </div>
    </div>
  );
}

/**
 * Wrapper con Provider de autenticación
 */
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

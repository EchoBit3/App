import Login from './Auth/Login';
import Register from './Auth/Register';
import History from './History';

/**
 * Contenedor de modales de autenticación e historial
 */
export default function AuthModals({
  showAuth,
  showHistory,
  authMode,
  isAuthenticated,
  onCloseAuth,
  onCloseHistory,
  onSwitchAuthMode,
  onAuthSuccess,
  onSelectQuery,
}) {
  return (
    <>
      {/* Auth Modal */}
      {showAuth && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={onCloseAuth}
        >
          <div 
            className="relative max-w-md w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={onCloseAuth}
              className="absolute -top-4 -right-4 w-10 h-10 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors z-10"
              aria-label="Cerrar"
            >
              ✕
            </button>
            {authMode === 'login' ? (
              <Login
                onSwitchToRegister={() => onSwitchAuthMode('register')}
                onSuccess={onAuthSuccess}
              />
            ) : (
              <Register
                onSwitchToLogin={() => onSwitchAuthMode('login')}
                onSuccess={onAuthSuccess}
              />
            )}
          </div>
        </div>
      )}

      {/* History Modal */}
      {showHistory && isAuthenticated && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={onCloseHistory}
        >
          <div 
            className="relative max-w-4xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={onCloseHistory}
              className="absolute top-4 right-4 w-10 h-10 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors z-10"
              aria-label="Cerrar"
            >
              ✕
            </button>
            <div className="overflow-y-auto max-h-[90vh]">
              <History onSelectQuery={onSelectQuery} />
            </div>
          </div>
        </div>
      )}
    </>
  );
}

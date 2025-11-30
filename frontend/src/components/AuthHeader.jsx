import { LogOut, User } from 'lucide-react';

/**
 * Header con autenticación integrada
 */
export default function AuthHeader({ 
  isAuthenticated, 
  user, 
  showSidebar, 
  setShowSidebar,
  onShowHistory,
  onShowAuth,
  onLogout 
}) {
  return (
    <header className="bg-white/10 backdrop-blur-md border-b border-white/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo y toggle sidebar */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="md:hidden p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
              aria-label="Toggle sidebar"
            >
              ☰
            </button>
            <h1 className="text-2xl md:text-3xl font-bold text-white">
              🎯 De-Mystify
            </h1>
          </div>

          {/* Auth buttons */}
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <button
                  onClick={onShowHistory}
                  className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-all flex items-center gap-2"
                  aria-label="Ver historial"
                >
                  📜 <span className="hidden sm:inline">Historial</span>
                </button>
                
                <div className="flex items-center gap-2 px-4 py-2 bg-white/20 rounded-lg">
                  <User className="w-4 h-4 text-white" />
                  <span className="text-white text-sm hidden md:inline">
                    {user?.username}
                  </span>
                </div>
                
                <button
                  onClick={onLogout}
                  className="px-4 py-2 bg-red-500/80 hover:bg-red-600 text-white rounded-lg transition-all flex items-center gap-2"
                  title="Cerrar sesión"
                  aria-label="Cerrar sesión"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden md:inline">Salir</span>
                </button>
              </>
            ) : (
              <button
                onClick={onShowAuth}
                className="px-6 py-2 bg-white hover:bg-gray-100 text-purple-600 font-semibold rounded-lg transition-all"
              >
                Iniciar Sesión
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

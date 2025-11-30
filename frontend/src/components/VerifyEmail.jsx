import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';

export default function VerifyEmail() {
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('');
  const [username, setUsername] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const verifyToken = async () => {
      // Obtener token de la URL
      const params = new URLSearchParams(location.search);
      const token = params.get('token');

      if (!token) {
        setStatus('error');
        setMessage('Token de verificación no encontrado');
        return;
      }

      try {
        const response = await fetch(`http://localhost:8001/api/auth/verify-email?token=${token}`);
        const data = await response.json();

        if (response.ok) {
          setStatus('success');
          setMessage(data.message || '¡Email verificado correctamente!');
          setUsername(data.username || '');
        } else {
          setStatus('error');
          setMessage(data.detail || 'Error al verificar el email');
        }
      } catch (err) {
        setStatus('error');
        setMessage('Error de conexión. Verifica que el servidor esté corriendo.');
      }
    };

    verifyToken();
  }, [location]);

  const handleGoToLogin = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-700 via-gray-800 to-slate-800 flex items-center justify-center p-4">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-slate-200/95 backdrop-blur-md rounded-2xl shadow-2xl w-full max-w-md p-8 border border-slate-300/50"
      >
        {status === 'verifying' && (
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Verificando email...</h2>
            <p className="text-gray-600">Por favor espera un momento</p>
          </div>
        )}

        {status === 'success' && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-center"
          >
            <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">¡Email Verificado!</h2>
            {username && (
              <p className="text-gray-600 mb-4">
                Bienvenido <span className="font-semibold text-purple-600">{username}</span>
              </p>
            )}
            <p className="text-gray-600 mb-6">{message}</p>
            <button
              onClick={handleGoToLogin}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg"
            >
              Ir a Iniciar Sesión
            </button>
          </motion.div>
        )}

        {status === 'error' && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-center"
          >
            <div className="w-16 h-16 bg-gradient-to-r from-red-500 to-rose-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Error de Verificación</h2>
            <p className="text-gray-600 mb-6">{message}</p>
            <div className="space-y-3">
              <button
                onClick={handleGoToLogin}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg"
              >
                Volver al Inicio
              </button>
              <p className="text-sm text-gray-500">
                ¿Necesitas ayuda? El token podría haber expirado (24 horas).
              </p>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}

// Reglas de validación para la aplicación
export const VALIDATION_RULES = {
  TASK: {
    MIN_LENGTH: 10,
    MAX_LENGTH: 2000,
  },
  USER: {
    USERNAME_MIN_LENGTH: 3,
    PASSWORD_MIN_LENGTH: 6,
  }
};

export const VALIDATION_MESSAGES = {
  TASK_EMPTY: 'Por favor, ingresa una tarea o instrucción para analizar.',
  TASK_TOO_SHORT: `La instrucción es demasiado corta (mínimo ${VALIDATION_RULES.TASK.MIN_LENGTH} caracteres). Proporciona más detalles.`,
  TASK_TOO_LONG: `La instrucción es demasiado larga (máximo ${VALIDATION_RULES.TASK.MAX_LENGTH} caracteres). Por favor, acórtala.`,
  AUTH_REQUIRED: 'Por favor inicia sesión para analizar tareas',
  API_ERROR: 'Error al procesar la tarea. Verifica que la API esté corriendo en http://localhost:8001',
};

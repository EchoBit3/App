# 🧩 Demystify

**Convierte instrucciones confusas en pasos claros y concretos.**

Una aplicación web diseñada para ayudar a personas neurodivergentes (autismo, TDAH) y cualquier persona que necesite clarificar tareas ambiguas en listas de pasos accionables.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

##  ¿Para qué sirve?

Imagina que te dicen: *"Haz un backup de tu computadora"*

Para muchas personas, esta instrucción es **confusa y abrumadora**:
- ¿Qué archivos debo respaldar?
- ¿Dónde los guardo?
- ¿Qué programa uso?
- ¿Cuál es el primer paso?

**Demystify** analiza esta instrucción con Inteligencia Artificial y te devuelve:

 **Pasos claros numerados:**
1. Conecta un disco duro externo
2. Abre la configuración de Windows
3. Busca "Backup"
4. ...

 **Información que falta:** "No especificaste qué archivos respaldar"

 **Preguntas para aclarar:** "¿Quieres respaldar solo documentos o todo el sistema?"

---

##  Características Principales

###  Diseñado para Neurodivergencia
- **Lenguaje claro y directo** (sin metáforas ni ambigüedades)
- **Pasos numerados** fáciles de seguir
- **Interfaz predecible** (botones siempre en el mismo lugar)
- **Sin animaciones distractoras** (modo reducido opcional)
- **Alto contraste** para mejor legibilidad

###  Seguridad y Privacidad
- **Autenticación segura**: Login con usuario/contraseña o Google
- **Encriptación**: Tus datos están protegidos
- **Rate limiting**: Protección contra ataques
- **Verificación de email**: Opcional pero recomendado

###  Funcionalidades
- **Historial**: Guarda tus análisis anteriores
- **Dashboard**: Estadísticas de uso
- **Exportar**: Descarga resultados en JSON/TXT
- **Responsive**: Funciona en móvil, tablet y computadora

---

##  Instalación Rápida

### Requisitos Previos
- **Python 3.9 o superior** → [Descargar aquí](https://www.python.org/downloads/)
- **Node.js 18 o superior** → [Descargar aquí](https://nodejs.org/)
- **Git** → [Descargar aquí](https://git-scm.com/)

### Paso 1: Clonar el proyecto
```bash
git clone https://github.com/tu-usuario/demystify.git
cd demystify
```

### Paso 2: Configurar el Backend
```bash
# Ir a la carpeta del backend
cd backend

# Instalar dependencias de Python
pip install -r requirements.txt

# Copiar archivo de configuración
cp .env.example .env

# Editar .env y agregar tu API key de Google Gemini
# (Instrucciones abajo)
```

### Paso 3: Configurar el Frontend
```bash
# Ir a la carpeta del frontend (nueva terminal)
cd frontend

# Instalar dependencias de Node.js
npm install
```

### Paso 4: Obtener API Key de Google Gemini (GRATIS)

1. Ve a: https://makersuite.google.com/app/apikey
2. Inicia sesión con tu cuenta Google
3. Click en **"Create API Key"**
4. Copia la key generada
5. Pégala en el archivo `backend/.env`:
   ```env
   GEMINI_API_KEY=tu-api-key-aqui
   ```

### Paso 5: Iniciar la aplicación

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
Servidor corriendo en: http://localhost:8001

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Aplicación corriendo en: http://localhost:3000

 **¡Listo!** Abre tu navegador en http://localhost:3000

---

##  Cómo Usar

### 1. Crear una cuenta
- Click en **"Registrarse"**
- Ingresa usuario, email y contraseña
- O usa **"Continuar con Google"** (más rápido)

### 2. Analizar una tarea
- Escribe tu instrucción confusa en el cuadro de texto
- Ejemplo: *"Necesito organizar mi escritorio"*
- Click en **"Analizar"**

### 3. Ver resultados
- **Pasos:** Lista numerada de qué hacer
- **Ambigüedades:** Qué información falta
- **Preguntas:** Qué aclarar para mejorar el análisis

### 4. Ver tu historial
- Click en el ícono de reloj (⏱️)
- Ve todos tus análisis anteriores
- Click en uno para volver a verlo

---

##  Estructura del Proyecto

```
demystify/
├── backend/              # Servidor API (Python/FastAPI)
│   ├── main.py          # Archivo principal
│   ├── auth.py          # Autenticación
│   ├── database.py      # Base de datos
│   ├── encryption.py    # Encriptación
│   └── requirements.txt # Dependencias Python
│
├── frontend/            # Interfaz web (React)
│   ├── src/
│   │   ├── components/  # Componentes visuales
│   │   ├── hooks/       # Lógica reutilizable
│   │   ├── services/    # Comunicación con API
│   │   └── App.jsx      # Componente principal
│   └── package.json     # Dependencias Node.js
│
├── shared/              # Código compartido
│   └── ai_service.py    # Servicio de IA (Gemini)
│
└── README.md            # Este archivo
```

---

## ⚙️ Configuración Avanzada

### Variables de Entorno (`.env`)

**Mínimo requerido:**
```env
GEMINI_API_KEY=tu-api-key-aqui
```

**Configuración completa:**
```env
# IA
GEMINI_API_KEY=tu-api-key-aqui

# Seguridad (generar para producción)
SECRET_KEY=genera-con-openssl-rand-hex-32
ENCRYPTION_KEY=genera-con-python-encryption-py

# OAuth Google (opcional)
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-client-secret

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
EMAIL_VERIFICATION_REQUIRED=false

# Base de datos
DATABASE_URL=sqlite:///./demystify.db
```

### Generar Claves de Seguridad

```bash
# SECRET_KEY (para JWT tokens)
openssl rand -hex 32

# ENCRYPTION_KEY (para encriptar datos)
cd backend
python encryption.py generate-key
```

---

## Tecnologías Usadas

### Backend
- **FastAPI** - Framework web moderno para Python
- **SQLAlchemy** - ORM para base de datos
- **Google Gemini** - Inteligencia Artificial
- **JWT** - Autenticación segura
- **Bcrypt** - Hashing de contraseñas

### Frontend
- **React 18** - Librería para interfaces
- **Vite** - Build tool ultra rápido
- **Tailwind CSS** - Estilos modernos
- **Framer Motion** - Animaciones suaves
- **Axios** - Cliente HTTP

### Seguridad
- **OAuth 2.0** - Login con Google
- **Encriptación AES** - Datos sensibles protegidos
- **Rate Limiting** - Protección contra ataques
- **CORS** - Configurado restrictivamente

---

##  Testing

```bash
# Backend tests
cd backend
pytest

# Linter
eslint src/
```

---

##  API Endpoints

### Autenticación
- `POST /api/auth/register` - Crear cuenta
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Usuario actual
- `GET /api/auth/google/login` - OAuth Google

### Análisis
- `POST /api/desambiguar` - Analizar tarea (requiere login)
- `GET /api/historial` - Ver historial
- `DELETE /api/historial/{id}` - Eliminar análisis

### Información
- `GET /api/health` - Estado del servidor
- `GET /api/stats` - Estadísticas
- `GET /api/ejemplos` - Ejemplos de uso

**Documentación completa:** http://localhost:8001/docs

---

##  Deploy a Producción

### Backend (Railway/Render)
1. Conecta tu repositorio GitHub
2. La plataforma detectará FastAPI automáticamente
3. Configura variables de entorno
4. Deploy automático

### Frontend (Vercel/Netlify)
1. Conecta tu repositorio
2. Build command: `npm run build`
3. Output directory: `dist`
4. Deploy automático

### Base de Datos
- **Desarrollo:** SQLite (ya incluido)
- **Producción:** PostgreSQL (recomendado)
  ```env
  DATABASE_URL=postgresql://user:pass@host/db
  ```

---

##  Contribuir

¡Las contribuciones son bienvenidas! 

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/mejora-increible`
3. Haz commit: `git commit -m "Agregar: mejora increíble"`
4. Push: `git push origin feature/mejora-increible`
5. Abre un Pull Request

### Reportar Bugs
Abre un [Issue](https://github.com/tu-usuario/demystify/issues) describiendo:
- Qué esperabas que pasara
- Qué pasó realmente
- Pasos para reproducir el error

---

##  Casos de Uso

### Para Personas Autistas
- Entender instrucciones vagas del trabajo/escuela
- Desglosar tareas del hogar
- Planificar actividades sociales

### Para Personas con TDAH
- Dividir proyectos grandes en pasos manejables
- Crear listas de tareas concretas
- Evitar procrastinación por abrumación

### Para Todos
- Clarificar emails confusos
- Planificar proyectos
- Organizar mudanzas
- Preparar eventos

---

##  Licencia

Este proyecto es software libre bajo la licencia **MIT**.

Puedes:
- ✅ Modificar
- ✅ Compartir (Sin fines de lucro)


Ver archivo [LICENSE](LICENSE) para más detalles.

---

##  Autor
EchoBit3
Creado con ❤️ para hacer la vida más fácil.

**Misión:** Ayudar a personas neurodivergentes a entender mejor las instrucciones del día a día.

---

## 🙏 Agradecimientos

- A mis docentes por siempre exigirnos dar lo mejor.
- A mis compañeros de segundo año por motivarme y compartir sus conocimientos.
- [FastAPI](https://fastapi.tiangolo.com/) - Framework increíble
- [React](https://react.dev/) - Librería poderosa
- [Google AI](https://ai.google.dev/) - API gratuita de Gemini
- [Tailwind CSS](https://tailwindcss.com/) - Estilos modernos
- Comunidad open source 💙

---

##  Soporte

¿Necesitas ayuda?

- Lee la documentación completa: http://localhost:8001/docs
- Reporta bugs: [Issues](https://github.com/tu-usuario/demystify/issues)
- Preguntas: [Discussions](https://github.com/tu-usuario/demystify/discussions)

---

##  Roadmap

### Próximas funcionalidades:
- [ ] App móvil nativa (iOS/Android)
- [ ] Modo offline completo
- [ ] Más idiomas (inglés, portugués)
- [ ] Plantillas predefinidas
- [ ] Integración con calendarios
- [ ] Recordatorios por email
- [ ] API pública para developers

---

**⭐ Si te gusta el proyecto, dale una estrella en GitHub!**

**🌟 Compártelo con quien lo necesite.**

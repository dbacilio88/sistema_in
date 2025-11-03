# Frontend Dashboard - Interfaz de Usuario

## 📋 Índice
- [Visión General](#visión-general)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Componentes Principales](#componentes-principales)
- [Vistas y Páginas](#vistas-y-páginas)
- [Funcionalidades](#funcionalidades)
- [Integración con Backend](#integración-con-backend)
- [Configuración](#configuración)

---

## 🎯 Visión General

El **Frontend Dashboard** es la interfaz web de usuario del sistema, desarrollada con **Next.js 14** y **React**. Proporciona una interfaz moderna y responsive para operadores, supervisores y administradores.

**Propósito:**
- Dashboard con métricas en tiempo real
- Visualización de infracciones
- Gestión de dispositivos
- Monitoreo de cámaras en vivo
- Reportes y analíticas
- Configuración del sistema

**Tecnologías:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- TailwindCSS
- Recharts (gráficos)
- Socket.io (WebSocket)

**Puerto:** 3000  
**URL:** `http://localhost:3000`

---

## 📁 Estructura del Proyecto

```
frontend-dashboard/
├── src/
│   ├── app/                         # App Router (Next.js 14)
│   │   ├── page.tsx                # Dashboard principal
│   │   ├── layout.tsx              # Layout global
│   │   ├── infractions/            # Gestión de infracciones
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── devices/                # Gestión de dispositivos
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── vehicles/               # Gestión de vehículos
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── reports/                # Reportes
│   │   │   └── page.tsx
│   │   ├── login/                  # Login
│   │   │   └── page.tsx
│   │   └── settings/               # Configuración
│   │       └── page.tsx
│   │
│   ├── components/                  # Componentes React
│   │   ├── DashboardHeader.tsx     # Header
│   │   ├── Sidebar.tsx             # Sidebar navigation
│   │   ├── RealtimeMetrics.tsx     # Métricas en tiempo real
│   │   ├── InfractionsTable.tsx    # Tabla de infracciones
│   │   ├── TrafficMap.tsx          # Mapa de tráfico
│   │   ├── AnalyticsCharts.tsx     # Gráficos y charts
│   │   ├── RealtimeMonitorView.tsx # Vista de cámaras
│   │   ├── DeviceCard.tsx          # Card de dispositivo
│   │   ├── InfractionCard.tsx      # Card de infracción
│   │   └── Settings.tsx            # Configuración
│   │
│   ├── lib/                         # Utilidades
│   │   ├── api.ts                  # Cliente API
│   │   ├── websocket.ts            # Cliente WebSocket
│   │   ├── auth.ts                 # Autenticación
│   │   └── utils.ts                # Helpers
│   │
│   ├── types/                       # TypeScript types
│   │   ├── infraction.ts
│   │   ├── device.ts
│   │   ├── vehicle.ts
│   │   └── user.ts
│   │
│   └── styles/                      # Estilos
│       └── globals.css
│
├── public/                          # Assets estáticos
│   ├── images/
│   └── icons/
│
├── next.config.ts                   # Configuración Next.js
├── tailwind.config.ts               # Configuración Tailwind
├── tsconfig.json                    # TypeScript config
├── package.json
└── Dockerfile
```

---

## 🧩 Componentes Principales

### 1. **DashboardHeader** 
**Archivo:** `src/components/DashboardHeader.tsx`

**Funcionalidad:**
- Muestra logo y título
- Indicador de conexión con backend
- Notificaciones en tiempo real
- Menú de usuario (perfil, logout)

**Props:**
```typescript
interface DashboardHeaderProps {
  isConnected: boolean;
}
```

---

### 2. **Sidebar**
**Archivo:** `src/components/Sidebar.tsx`

**Funcionalidad:**
- Navegación principal
- Tabs activas destacadas
- Enlaces a secciones:
  - 📊 Dashboard
  - 🚨 Infracciones
  - 📹 Dispositivos
  - 🚗 Vehículos
  - 📈 Reportes
  - ⚙️ Configuración

**Props:**
```typescript
interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}
```

---

### 3. **RealtimeMetrics**
**Archivo:** `src/components/RealtimeMetrics.tsx`

**Funcionalidad:**
- Tarjetas con métricas clave en tiempo real
- Actualización vía WebSocket
- Animaciones de cambio

**Métricas mostradas:**
```typescript
interface Metrics {
  totalInfractions: number;
  pendingReview: number;
  activeDevices: number;
  totalVehicles: number;
  todayInfractions: number;
  criticalAlerts: number;
}
```

**Visualización:**
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Infracciones Hoy │  │ Pendientes       │  │ Dispositivos     │
│      127         │  │     42           │  │   Activos: 8/10  │
│  ↑ 15% vs ayer  │  │  (Ver detalles)  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

### 4. **InfractionsTable**
**Archivo:** `src/components/InfractionsTable.tsx`

**Funcionalidad:**
- Tabla con infracciones recientes
- Filtros por:
  - Estado (pendiente, validada, rechazada)
  - Tipo (velocidad, carril, luz roja, etc.)
  - Fecha
  - Zona
  - Dispositivo
- Ordenamiento por columnas
- Paginación
- Acciones:
  - Ver detalle
  - Validar
  - Rechazar
  - Exportar

**Columnas:**
- ID
- Fecha/Hora
- Tipo
- Placa
- Velocidad (si aplica)
- Zona
- Estado
- Severidad
- Acciones

**Props:**
```typescript
interface InfractionsTableProps {
  initialData?: Infraction[];
  filters?: InfractionFilters;
  onRowClick?: (infraction: Infraction) => void;
}
```

---

### 5. **TrafficMap**
**Archivo:** `src/components/TrafficMap.tsx`

**Funcionalidad:**
- Mapa interactivo con ubicaciones
- Marcadores de:
  - Cámaras/dispositivos
  - Zonas de monitoreo
  - Infracciones recientes
- Click en marcador → Ver detalles
- Mapa de calor de infracciones

**Tecnología:** Leaflet o Google Maps API

**Props:**
```typescript
interface TrafficMapProps {
  devices: Device[];
  infractions: Infraction[];
  zones: Zone[];
  center?: [number, number];
  zoom?: number;
}
```

---

### 6. **AnalyticsCharts**
**Archivo:** `src/components/AnalyticsCharts.tsx`

**Funcionalidad:**
- Gráficos estadísticos
- Tipos de gráficos:
  - **Línea:** Infracciones por hora/día/semana
  - **Barra:** Infracciones por tipo
  - **Torta:** Distribución por severidad
  - **Área:** Tendencias

**Tecnología:** Recharts

**Ejemplo - Infracciones por hora:**
```tsx
<LineChart data={hourlyData}>
  <XAxis dataKey="hour" />
  <YAxis />
  <Line type="monotone" dataKey="infractions" stroke="#8884d8" />
  <Tooltip />
  <Legend />
</LineChart>
```

---

### 7. **RealtimeMonitorView**
**Archivo:** `src/components/RealtimeMonitorView.tsx`

**Funcionalidad:**
- Vista de múltiples cámaras en grid
- Streaming en vivo (RTSP → WebRTC/HLS)
- Overlays con información:
  - Vehículos detectados
  - Velocidad
  - Placas reconocidas
- Controles:
  - Play/Pause
  - Fullscreen
  - PTZ (si disponible)

**Layout:**
```
┌─────────────┬─────────────┐
│  Cámara 1   │  Cámara 2   │
│  (ZN001)    │  (ZN002)    │
│  🟢 Activa  │  🟢 Activa  │
└─────────────┴─────────────┘
┌─────────────┬─────────────┐
│  Cámara 3   │  Cámara 4   │
│  (ZN003)    │  (ZN004)    │
│  🔴 Offline │  🟢 Activa  │
└─────────────┴─────────────┘
```

---

### 8. **DeviceCard**
**Archivo:** `src/components/DeviceCard.tsx`

**Funcionalidad:**
- Tarjeta visual de dispositivo
- Información:
  - Nombre y código
  - Estado (activo, inactivo, mantenimiento, error)
  - Ubicación
  - Última conexión
  - Estadísticas (infracciones detectadas)
- Acciones:
  - Ver detalles
  - Iniciar/Detener stream
  - Configurar
  - Ver en mapa

**Props:**
```typescript
interface DeviceCardProps {
  device: Device;
  onStart?: (deviceId: string) => void;
  onStop?: (deviceId: string) => void;
  onConfigure?: (deviceId: string) => void;
}
```

---

### 9. **InfractionCard**
**Archivo:** `src/components/InfractionCard.tsx`

**Funcionalidad:**
- Tarjeta expandida de infracción
- Muestra:
  - Snapshot con vehículo
  - Detalles (tipo, fecha, placa, velocidad)
  - Evidencia (video, imágenes)
  - Estado y severidad
- Acciones:
  - Validar
  - Rechazar
  - Ver video completo
  - Exportar reporte

---

## 📱 Vistas y Páginas

### 1. **Dashboard Principal** (`/`)
**Archivo:** `src/app/page.tsx`

**Contenido:**
- `RealtimeMetrics` - Métricas en tiempo real
- `InfractionsTable` - Últimas infracciones
- `TrafficMap` - Mapa de infracciones
- `AnalyticsCharts` - Gráficos del día

**Actualización:** WebSocket cada 5 segundos

---

### 2. **Infracciones** (`/infractions`)
**Archivo:** `src/app/infractions/page.tsx`

**Funcionalidades:**
- Listado completo con filtros avanzados
- Búsqueda por placa
- Ordenamiento múltiple
- Acciones en lote (validar múltiples)
- Exportar a PDF/Excel

**Detalle de infracción** (`/infractions/[id]`)
- Vista detallada con toda la información
- Galería de evidencia
- Timeline de eventos
- Formulario de validación/rechazo
- Historial de cambios

---

### 3. **Dispositivos** (`/devices`)
**Archivo:** `src/app/devices/page.tsx`

**Funcionalidades:**
- Grid de tarjetas de dispositivos
- Filtro por estado
- Vista de mapa
- Control de streams
- Agregar nuevo dispositivo

**Detalle de dispositivo** (`/devices/[id]`)
- Información técnica
- Configuración RTSP
- Calibración de cámara
- Estadísticas de detección
- Logs de actividad

---

### 4. **Vehículos** (`/vehicles`)
**Archivo:** `src/app/vehicles/page.tsx`

**Funcionalidades:**
- Búsqueda por placa
- Listado de vehículos
- Datos de SUNARP
- Historial de infracciones
- Vehículos en lista negra

**Detalle de vehículo** (`/vehicles/[id]`)
- Información del propietario
- Historial completo de infracciones
- Gráficos de comportamiento
- Alertas y notificaciones

---

### 5. **Reportes** (`/reports`)
**Archivo:** `src/app/reports/page.tsx`

**Funcionalidades:**
- Generación de reportes personalizados
- Filtros:
  - Rango de fechas
  - Tipo de infracción
  - Zona
  - Dispositivo
- Formatos: PDF, Excel, CSV
- Gráficos interactivos
- Reportes programados

**Tipos de reportes:**
- Diario
- Semanal
- Mensual
- Por zona
- Por dispositivo
- Por tipo de infracción

---

### 6. **Configuración** (`/settings`)
**Archivo:** `src/app/settings/page.tsx`

**Secciones:**
- **General**
  - Nombre del sistema
  - Logo
  - Idioma
- **Usuarios**
  - Gestión de usuarios
  - Roles y permisos
- **Notificaciones**
  - Configurar alertas
  - Canales (email, push, SMS)
- **Zonas**
  - Definir zonas de monitoreo
  - Límites de velocidad
- **Integrations**
  - API keys
  - Webhooks
  - SUNARP credentials

---

## ⚙️ Funcionalidades

### 1. **Autenticación**
**Flujo:**
1. Usuario ingresa credenciales en `/login`
2. Frontend envía `POST /api/auth/login/`
3. Backend retorna JWT (access + refresh)
4. Frontend guarda tokens en localStorage
5. Todas las requests incluyen `Authorization: Bearer <token>`

**Protección de rutas:**
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('token');
  if (!token && !request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}
```

---

### 2. **Notificaciones en Tiempo Real**
**Tecnología:** WebSocket (Socket.io)

**Conexión:**
```typescript
import io from 'socket.io-client';

const socket = io('http://localhost:8000', {
  auth: {
    token: localStorage.getItem('token')
  }
});

socket.on('notification', (data) => {
  // Mostrar notificación toast
  toast.success(data.message);
  
  // Actualizar métricas
  refreshMetrics();
});

socket.on('infraction.detected', (infraction) => {
  // Agregar a tabla
  addInfractionToTable(infraction);
  
  // Reproducir sonido
  playAlertSound();
});
```

**Eventos escuchados:**
- `notification` - Notificaciones generales
- `infraction.detected` - Nueva infracción
- `device.status` - Cambio de estado de dispositivo
- `metrics.update` - Actualización de métricas

---

### 3. **Cliente API**
**Archivo:** `src/lib/api.ts`

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para agregar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para renovar token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expirado, renovar
      const refreshToken = localStorage.getItem('refreshToken');
      const response = await axios.post('/auth/refresh/', {
        refresh: refreshToken
      });
      localStorage.setItem('token', response.data.access);
      // Reintentar request original
      return api(error.config);
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

### 4. **Gestión de Estado**
**Opciones:**
- **Context API** (React) - Para estado global simple
- **Zustand** - State management ligero
- **React Query** - Para cacheo de datos del backend

**Ejemplo con Context:**
```typescript
// contexts/AuthContext.tsx
export const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  const login = async (username: string, password: string) => {
    const response = await api.post('/auth/login/', { username, password });
    setUser(response.data.user);
    setIsAuthenticated(true);
    localStorage.setItem('token', response.data.access);
  };
  
  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login }}>
      {children}
    </AuthContext.Provider>
  );
}
```

---

### 5. **Responsive Design**
**Breakpoints TailwindCSS:**
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

**Ejemplo:**
```tsx
<div className="
  grid 
  grid-cols-1 
  md:grid-cols-2 
  lg:grid-cols-3 
  xl:grid-cols-4 
  gap-4
">
  {/* Cards responsivas */}
</div>
```

---

## 🔗 Integración con Backend

### Consumo de APIs

#### 1. Obtener infracciones
```typescript
const fetchInfractions = async (filters?: InfractionFilters) => {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.type) params.append('infraction_type', filters.type);
  if (filters?.dateFrom) params.append('date_from', filters.dateFrom);
  
  const response = await api.get(`/infractions/?${params}`);
  return response.data;
};
```

#### 2. Validar infracción
```typescript
const validateInfraction = async (id: string, notes: string) => {
  const response = await api.post(`/infractions/${id}/validate/`, {
    review_notes: notes
  });
  return response.data;
};
```

#### 3. Controlar dispositivo
```typescript
const startDevice = async (deviceId: string) => {
  const response = await api.post(`/devices/${deviceId}/start/`);
  return response.data;
};

const stopDevice = async (deviceId: string) => {
  const response = await api.post(`/devices/${deviceId}/stop/`);
  return response.data;
};
```

---

## 🔧 Configuración

### Variables de Entorno (`.env.local`)

```bash
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE=/api

# WebSocket
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Features
NEXT_PUBLIC_ENABLE_REALTIME=true
NEXT_PUBLIC_ENABLE_MAP=true

# Google Maps (si se usa)
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-api-key

# Otros
NEXT_PUBLIC_APP_NAME=Sistema de Detección de Infracciones
NEXT_PUBLIC_COMPANY_NAME=Tu Empresa
```

---

### Comandos

```bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build producción
npm run build

# Iniciar producción
npm start

# Lint
npm run lint

# Type check
npm run type-check
```

---

## 📊 Responsabilidades

### ✅ Sí gestiona:
- Interfaz de usuario
- Visualización de datos
- Interacción con usuario
- Consumo de API REST
- WebSocket para tiempo real
- Validación de formularios
- Navegación

### ❌ No gestiona:
- Detección de infracciones (→ ML Service)
- Procesamiento de video (→ Inference Service)
- Persistencia de datos (→ Backend Django)
- Lógica de negocio (→ Backend)

---

**Ver también:**
- [ARQUITECTURA.md](./ARQUITECTURA.md) - Visión general
- [BACKEND-DJANGO.md](./BACKEND-DJANGO.md) - API REST
- [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md) - Flujos

---

**Última actualización:** Noviembre 2025

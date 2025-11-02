# Dashboard Frontend - Sistema de Detección de Infracciones

## 🎯 Overview

Dashboard interactivo en tiempo real para monitorear el sistema de detección de infracciones de tránsito. Construido con Next.js 15, TypeScript y Tailwind CSS.

## ✨ Características

### 📊 Métricas en Tiempo Real
- **Cámaras Activas**: Monitoreo del estado de todas las cámaras
- **Infracciones Detectadas**: Contador en tiempo real de infracciones del día
- **Tiempo de Procesamiento**: Latencia promedio del sistema
- **Vehículos Detectados**: Total de vehículos procesados

### 📋 Gestión de Infracciones
- **Tabla Interactiva**: Lista de infracciones con filtros y paginación
- **Detalles Completos**: ID, placa, tipo, ubicación, fecha/hora
- **Estados de Severidad**: Alta, Media, Baja con códigos de color
- **Estados de Procesamiento**: Pendiente, Procesado, Resuelto
- **Acciones Rápidas**: Ver detalles y evidencia fotográfica

### 🗺️ Mapa de Tráfico
- **Ubicaciones en Tiempo Real**: Posición de cámaras e infracciones
- **Estados Visuales**: Indicadores de color por estado
- **Información Contextual**: Datos al hacer clic en ubicaciones
- **Leyenda Interactiva**: Explicación de símbolos y colores

### 📈 Análisis y Reportes
- **Gráficos Temporales**: Tendencias de infracciones por día
- **Distribución por Tipo**: Pie chart de tipos de infracciones
- **Patrones Horarios**: Análisis de picos de tráfico
- **Métricas de Rendimiento**: Precisión, latencia y uptime del sistema

## 🛠️ Stack Tecnológico

- **Framework**: Next.js 15 con App Router
- **Lenguaje**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Heroicons
- **Date Handling**: date-fns
- **WebSocket**: Socket.io-client (preparado)
- **HTTP Client**: Fetch API nativo

## 🚀 Instalación y Uso

### Prerrequisitos
- Node.js 18+ 
- npm o yarn

### Pasos de Instalación

1. **Navegar al directorio**:
   ```bash
   cd frontend-dashboard/
   ```

2. **Instalar dependencias**:
   ```bash
   npm install
   ```

3. **Iniciar servidor de desarrollo**:
   ```bash
   npm run dev
   # o usar el script incluido:
   ./start-dashboard.sh
   ```

4. **Acceder al dashboard**:
   - URL: http://localhost:3000
   - El dashboard se abrirá automáticamente en el navegador

### Scripts Disponibles

```bash
# Desarrollo
npm run dev          # Servidor de desarrollo con hot-reload

# Producción
npm run build        # Build optimizado para producción
npm run start        # Servidor de producción

# Linting y formato
npm run lint         # ESLint
npm run type-check   # TypeScript check
```

## 📱 Interfaz de Usuario

### Layout Principal
```
┌─────────────┬─────────────────────────────────┐
│             │        Header                   │
│   Sidebar   ├─────────────────────────────────┤
│             │                                 │
│ - Overview  │        Main Content             │
│ - Infractions│                                │
│ - Analytics │        Dashboard Views          │
│ - Map       │                                 │
│ - Settings  │                                 │
└─────────────┴─────────────────────────────────┘
```

## 🔌 Integración con Backend

### APIs Esperadas

El frontend está preparado para conectarse con las siguientes APIs:

```typescript
// Endpoints REST
GET /api/metrics              // Métricas en tiempo real
GET /api/infractions         // Lista de infracciones
GET /api/infractions/:id     // Detalle de infracción
GET /api/cameras             // Estado de cámaras
GET /api/analytics/daily     // Datos analíticos diarios
GET /api/analytics/hourly    // Datos analíticos por hora

// WebSocket Events
connect: /ws/dashboard       // Conexión en tiempo real
events:
  - new_infraction           // Nueva infracción detectada
  - metrics_update           // Actualización de métricas
  - camera_status_change     // Cambio de estado de cámara
  - system_alert             // Alertas del sistema
```

## 🧪 Testing

### Preparación para Tests
```bash
# Instalar dependencias de testing
npm install --save-dev @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom

# Configurar Jest
npx jest --init
```

## 📋 Roadmap

### Fase Actual ✅ COMPLETADA
- [x] Estructura base del proyecto
- [x] Componentes principales del dashboard
- [x] Navegación y layout responsive
- [x] Gráficos y visualizaciones
- [x] Simulación de datos en tiempo real

### Próximas Fases 🚧
- [ ] Integración WebSocket real
- [ ] Conexión con APIs del backend
- [ ] Autenticación y autorización
- [ ] Filtros avanzados y búsqueda
- [ ] Exportación de reportes
- [ ] Notificaciones push
- [ ] Modo offline
- [ ] PWA capabilities

---

**Versión**: 1.0.0  
**Última Actualización**: 2025-01-01  
**Maintainer**: Equipo Frontend

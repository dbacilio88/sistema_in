# Sistema de Monitoreo en Tiempo Real

## Características Implementadas

### 🎥 **Gestión de Cámaras por Zona**
- Visualización de cámaras organizadas por zonas geográficas
- Filtrado de cámaras por zona específica o todas las zonas
- Información detallada de cada cámara (nombre, código, estado, resolución)

### 📊 **Panel de Estadísticas**
- Contador total de cámaras disponibles
- Número de cámaras activas
- Cámaras transmitiendo en tiempo real
- Cámaras seleccionadas para transmisión

### 🔍 **Filtros Avanzados**
- **Por Zona**: Filtrar cámaras por zona específica
- **Por Estado**: Filtrar por estado (activas, inactivas, en mantenimiento, con error)
- Selección múltiple de cámaras
- Función "Seleccionar Todas" para filtros aplicados

### 📺 **Transmisión en Tiempo Real**
- Visualización de streams RTSP de cámaras individuales
- Vista de grilla para múltiples transmisiones simultáneas
- Modo pantalla completa para visualización detallada
- Controles de reproducción/pausa por cámara

### 🎛️ **Controles de Transmisión**
- Iniciar/detener transmisiones individuales
- Iniciar transmisión de cámaras seleccionadas
- Detener todas las transmisiones activas
- Vista de transmisiones múltiples con navegación

### 🔄 **Actualización Automática**
- Refresh automático de datos cada 30 segundos
- Botón de actualización manual
- Sincronización en tiempo real del estado de cámaras

### 🎨 **Interfaz de Usuario**
- Diseño responsivo para diferentes tamaños de pantalla
- Vista de grilla adaptativa (1-4 columnas según número de cámaras)
- Indicadores visuales de estado de cámaras
- Tema oscuro para modo pantalla completa

## Componentes Técnicos

### **RealtimeMonitorView.tsx**
Componente principal que orchestea toda la funcionalidad del monitoreo.

### **VideoPlayer.tsx**
Componente especializado para reproducir streams de video con:
- Manejo de errores de conexión
- Controles de pantalla completa
- Overlay con información de dispositivo

### **MultiStreamView.tsx**
Vista especializada para múltiples transmisiones con:
- Layout de grilla adaptativo
- Modo pantalla completa
- Vista detallada de streams individuales

### **useCameraStreams.ts**
Hook personalizado que maneja:
- Estado de cámaras y zonas
- Lógica de transmisiones
- Filtros y selecciones
- Actualizaciones automáticas

## Estructura de Datos

### **Device (Cámara)**
```typescript
interface Device {
  id: string;
  code: string;           // Código único (ej: CAM001)
  name: string;           // Nombre descriptivo
  device_type: string;    // Tipo de dispositivo
  status: string;         // Estado (active, inactive, maintenance, error)
  zone_name: string;      // Nombre de la zona
  location_lat: string;   // Latitud GPS
  location_lon: string;   // Longitud GPS
  ip_address: string;     // Dirección IP
  resolution: string;     // Resolución (ej: 1920x1080)
  fps: number;           // Frames por segundo
  is_active: boolean;    // Activo/Inactivo
}
```

### **Zone (Zona)**
```typescript
interface Zone {
  id: string;
  code: string;           // Código único (ej: ZN001)
  name: string;           // Nombre de la zona
  speed_limit: number;    // Límite de velocidad
  is_active: boolean;     // Activa/Inactiva
  device_count: number;   // Número de dispositivos
}
```

### **CameraStream**
```typescript
interface CameraStream {
  deviceId: string;       // ID del dispositivo
  isStreaming: boolean;   // Estado de transmisión
  streamUrl: string;      // URL del stream RTSP
}
```

## APIs Utilizadas

### **Backend Django**
- `GET /api/devices/` - Obtener lista de dispositivos
- `GET /api/devices/zones/` - Obtener lista de zonas
- `GET /api/devices/{id}/stream/` - Stream RTSP de cámara específica
- `GET /api/devices/{id}/stream_info/` - Información del stream

### **Filtros Disponibles**
- `status`: active, inactive, maintenance, error
- `device_type`: camera, sensor, radar
- `zone`: ID de zona específica
- `limit`: Número máximo de resultados

## Funcionalidades Avanzadas

### **Manejo de Errores**
- Detección automática de streams desconectados
- Reintento automático de conexiones
- Mensajes de error informativos
- Fallback a placeholder cuando falla la conexión

### **Optimización de Performance**
- Lazy loading de streams
- Limpieza automática de conexiones inactivas
- Debounce en filtros y búsquedas
- Memoización de componentes pesados

### **Experiencia de Usuario**
- Loading states durante cargas
- Feedback visual de acciones
- Tooltips informativos
- Atajos de teclado (en desarrollo)

## Configuración Requerida

### **Variables de Entorno**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # URL del backend Django
```

### **Dependencias**
- Next.js 14+
- React 18+
- Heroicons
- Tailwind CSS
- TypeScript

## Próximas Características

- [ ] Grabación de streams
- [ ] Detección de movimiento
- [ ] Alertas en tiempo real
- [ ] Análisis de tráfico con IA
- [ ] Exportación de videos
- [ ] Notificaciones push
- [ ] Configuración de cámaras desde la interfaz
- [ ] Dashboard de métricas de performance

## Uso del Sistema

1. **Seleccionar Zona**: Elegir zona específica o todas las zonas
2. **Aplicar Filtros**: Filtrar por estado de cámaras
3. **Seleccionar Cámaras**: Click en cámaras individuales o "Seleccionar Todas"
4. **Iniciar Transmisión**: Usar botón "Iniciar Transmisión"
5. **Gestionar Streams**: Usar controles individuales o vista múltiple
6. **Pantalla Completa**: Click en expand para vista completa
7. **Detener**: Usar controles individuales o "Detener Todas"

El sistema está diseñado para ser intuitivo y escalable, soportando desde unas pocas cámaras hasta cientos de dispositivos distribuidos en múltiples zonas.
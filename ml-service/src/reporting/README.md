# Reporting and Dashboard System

Este módulo proporciona un sistema completo de reportes y dashboards para el análisis de tráfico en tiempo real.

## Características Principales

### 📊 Generación de Reportes
- **Reportes Diarios**: Resúmenes ejecutivos con métricas clave
- **Análisis Semanales**: Tendencias y patrones de tráfico
- **Reportes Mensuales**: Análisis comprensivo con estadísticas detalladas
- **Análisis de Violaciones**: Tendencias de infracciones por tipo y dispositivo
- **Rendimiento de Dispositivos**: Métricas de uptime, FPS y precisión
- **Flujo de Tráfico**: Análisis de patrones de circulación

### 🎯 Dashboard en Tiempo Real
- **Métricas en Vivo**: Actualización automática cada 5 segundos
- **Gráficos Interactivos**: Visualizaciones dinámicas con Plotly
- **Sistema de Alertas**: Notificaciones automáticas por anomalías
- **Monitor de Dispositivos**: Estado en tiempo real de cámaras
- **Interface Web**: Dashboard responsivo con diseño moderno

### 📈 Visualización Avanzada
- **Múltiples Temas**: Claro, oscuro, mínimal, profesional
- **Gráficos Interactivos**: Plotly para exploración de datos
- **Mapas de Calor**: Distribución temporal y geográfica
- **Análisis de Tendencias**: Regresión lineal y proyecciones
- **Distribuciones Estadísticas**: Histogramas con overlays

### 🔌 API REST Completa
- **Generación de Reportes**: Endpoints para todos los tipos
- **Datos en Tiempo Real**: Métricas actualizadas
- **Exportación**: CSV, JSON, Excel
- **Gestión de Alertas**: Reconocimiento y resolución
- **Templates de Gráficos**: Configuraciones predefinidas

## Arquitectura del Sistema

```
src/reporting/
├── __init__.py              # Módulo principal
├── report_generator.py      # Generador de reportes
├── dashboard_service.py     # Servicio de dashboard web
├── visualization_utils.py   # Utilidades de visualización
├── api_server.py           # Servidor API REST
└── README.md               # Esta documentación
```

### Componentes Principales

#### 1. ReportGenerator
Genera reportes automáticamente basados en configuración:

```python
from reporting import ReportGenerator, ReportConfig, ReportType

# Configurar reporte
config = ReportConfig(
    report_type=ReportType.DAILY_SUMMARY,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 2),
    include_charts=True,
    output_format="html"
)

# Generar reporte
generator = ReportGenerator(storage_service)
report = await generator.generate_report(config)
```

#### 2. DashboardService
Servicio web completo con WebSocket para tiempo real:

```python
from reporting import DashboardService

# Iniciar dashboard
dashboard = DashboardService(storage_service, port=8080)
await dashboard.start()
```

#### 3. AdvancedChartGenerator
Generación de gráficos avanzados con múltiples bibliotecas:

```python
from reporting import AdvancedChartGenerator, ChartConfig, VisualizationTheme

# Configurar generador
config = ChartConfig(
    theme=VisualizationTheme.PROFESSIONAL,
    width=1000,
    height=600,
    interactive=True
)

generator = AdvancedChartGenerator(config)
chart = generator.create_violation_heatmap(data)
```

#### 4. ReportingAPIServer
API REST para integración con otros sistemas:

```python
from reporting import ReportingAPIServer

# Iniciar API
api = ReportingAPIServer(storage_service, port=8081)
await api.start()
```

## Tipos de Reportes

### 📅 Reporte Diario (DAILY_SUMMARY)
- Resumen ejecutivo del día
- Métricas clave de tráfico y violaciones
- Gráficos de distribución horaria
- Estado de dispositivos

### 📊 Análisis Semanal (WEEKLY_ANALYSIS)
- Tendencias día a día
- Comparación con semanas anteriores
- Patrones de tráfico por día de semana
- Tabla detallada por día

### 📈 Reporte Mensual (MONTHLY_REPORT)
- Análisis comprensivo del mes
- Mapa de calor hora/día
- Rendimiento detallado de dispositivos
- Estadísticas de violaciones

### 🚨 Tendencias de Violaciones (VIOLATION_TRENDS)
- Análisis por tipo de violación
- Distribución por dispositivo
- Patrones horarios
- Tasa de resolución

### 🖥️ Rendimiento de Dispositivos (DEVICE_PERFORMANCE)
- Uptime por dispositivo
- FPS promedio
- Precisión de detección
- Errores y mantenimiento

### 🚗 Flujo de Tráfico (TRAFFIC_FLOW)
- Distribución horaria del tráfico
- Tipos de vehículos
- Velocidades promedio
- Análisis de congestión

## Dashboard Web

### Características
- **Tiempo Real**: Actualización automática cada 5 segundos
- **Responsive**: Adaptable a móviles y tablets
- **Interactivo**: Gráficos explorables con zoom y filtros
- **Alertas**: Sistema de notificaciones en tiempo real
- **Exportación**: Descarga de reportes directamente

### Métricas en Tiempo Real
- Vehículos detectados hoy
- Violaciones registradas
- Dispositivos activos
- Velocidad promedio
- Estado de cada cámara

### Gráficos Interactivos
- Distribución de violaciones por tipo (pie chart)
- Tráfico horario (line chart)
- Mapa de calor de actividad
- Rendimiento de dispositivos

## Sistema de Alertas

### Tipos de Alertas
- **INFO**: Información general del sistema
- **WARNING**: Situaciones que requieren atención
- **ERROR**: Errores que afectan funcionalidad
- **CRITICAL**: Fallos críticos del sistema

### Alertas Automáticas
- Dispositivo desconectado
- Alta tasa de violaciones
- Degradación de rendimiento
- Errores del sistema
- Capacidad de almacenamiento

### Gestión de Alertas
```python
# Reconocer alerta
POST /api/alerts/{alert_id}/acknowledge

# Resolver alerta
POST /api/alerts/{alert_id}/resolve

# Listar alertas activas
GET /api/alerts
```

## API REST Endpoints

### Métricas
```bash
# Métricas en tiempo real
GET /api/v1/metrics

# Historial de métricas
GET /api/v1/metrics/history?start_date=2024-01-01&end_date=2024-01-02&interval=hour
```

### Reportes
```bash
# Generar reporte
POST /api/v1/reports/generate
{
  "report_type": "daily_summary",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-01T23:59:59Z",
  "include_charts": true
}

# Listar reportes
GET /api/v1/reports?limit=10&offset=0

# Descargar reporte
GET /api/v1/reports/{report_id}/download

# Vista previa HTML
GET /api/v1/reports/{report_id}/preview
```

### Gráficos
```bash
# Generar gráfico personalizado
POST /api/v1/charts/generate
{
  "chart_type": "heatmap",
  "data": {...},
  "title": "Mi Gráfico",
  "theme": "professional",
  "interactive": true
}

# Templates disponibles
GET /api/v1/charts/templates
```

### Exportación
```bash
# Exportar violaciones
GET /api/v1/export/violations?start_date=2024-01-01&end_date=2024-01-02&format=csv

# Formatos: csv, json, excel
```

## Configuración

### Variables de Entorno
```bash
# Puerto del dashboard
DASHBOARD_PORT=8080

# Puerto de la API
API_PORT=8081

# Tema por defecto
DEFAULT_THEME=professional

# Intervalo de actualización (segundos)
REFRESH_INTERVAL=5

# Retención de alertas (horas)
ALERT_RETENTION_HOURS=24
```

### Configuración de Reportes
```python
DEFAULT_REPORT_CONFIG = ReportConfig(
    report_type=ReportType.DAILY_SUMMARY,
    include_charts=True,
    output_format="html",
    chart_style="professional",
    language="es"
)
```

### Configuración de Dashboard
```python
DEFAULT_DASHBOARD_CONFIG = DashboardConfig(
    refresh_interval=5,
    chart_update_interval=10,
    auto_refresh=True,
    theme="light",
    layout="default"
)
```

## Uso Práctico

### 1. Iniciar Dashboard Completo
```python
import asyncio
from reporting import DashboardService

async def main():
    # Iniciar dashboard con storage service
    dashboard = DashboardService(storage_service, port=8080)
    await dashboard.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Generar Reporte Programático
```python
from datetime import datetime, timedelta
from reporting import ReportGenerator, ReportConfig, ReportType

async def generate_daily_report():
    generator = ReportGenerator(storage_service)
    
    config = ReportConfig(
        report_type=ReportType.DAILY_SUMMARY,
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now(),
        include_charts=True
    )
    
    report = await generator.generate_report(config)
    
    # Guardar reporte
    with open(f"daily_report_{datetime.now().strftime('%Y%m%d')}.html", 'w') as f:
        f.write(report['html_content'])
```

### 3. API Server Independiente
```python
import asyncio
from reporting import ReportingAPIServer

async def main():
    api = ReportingAPIServer(storage_service, port=8081)
    await api.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Gráficos Personalizados
```python
from reporting import AdvancedChartGenerator, ChartConfig, VisualizationTheme

# Configurar generador
config = ChartConfig(
    theme=VisualizationTheme.DARK,
    width=1200,
    height=800,
    interactive=True
)

generator = AdvancedChartGenerator(config)

# Datos de ejemplo
violation_data = {
    'cam_001': {str(h): h * 2 for h in range(24)},
    'cam_002': {str(h): h * 3 for h in range(24)}
}

# Generar mapa de calor
heatmap = generator.create_violation_heatmap(violation_data)

# El resultado es una imagen en base64 o JSON para Plotly
```

## Dependencias

### Bibliotecas Principales
```txt
fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=12.0
pandas>=2.1.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.17.0
jinja2>=3.1.0
pydantic>=2.5.0
```

### Dependencias Opcionales
```txt
openpyxl>=3.1.0    # Para exportación Excel
fpdf2>=2.7.0       # Para generación PDF
reportlab>=4.0.0   # Para reportes PDF avanzados
```

## Extensibilidad

### Nuevos Tipos de Reportes
```python
# 1. Agregar nuevo tipo en ReportType enum
class ReportType(Enum):
    CUSTOM_ANALYSIS = "custom_analysis"

# 2. Implementar método en ReportGenerator
async def _generate_custom_analysis(self, config: ReportConfig):
    # Lógica personalizada
    pass

# 3. Agregar al switch en generate_report
```

### Nuevos Tipos de Gráficos
```python
# Agregar método en AdvancedChartGenerator
def create_custom_chart(self, data, title):
    # Implementación personalizada
    pass
```

### Alertas Personalizadas
```python
# Agregar nuevo tipo de alerta
class AlertType(Enum):
    CUSTOM_ALERT = "custom_alert"

# Implementar lógica en _check_alerts
```

## Monitoreo y Logs

### Logs del Sistema
```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('reporting')
```

### Métricas de Rendimiento
- Tiempo de generación de reportes
- Memoria utilizada por gráficos
- Conexiones WebSocket activas
- Latencia de API endpoints

## Mejores Prácticas

### 1. Configuración
- Usar variables de entorno para configuración
- Validar parámetros de entrada
- Implementar timeouts apropiados

### 2. Rendimiento
- Cachear gráficos cuando sea posible
- Usar paginación para grandes datasets
- Implementar compresión para respuestas grandes

### 3. Seguridad
- Validar todos los inputs de usuario
- Implementar rate limiting en API
- Usar HTTPS en producción

### 4. Mantenimiento
- Limpiar reportes antiguos automáticamente
- Rotar logs regularmente
- Monitorear uso de memoria y CPU

## Solución de Problemas

### Problemas Comunes

#### 1. Gráficos no se generan
```bash
# Verificar dependencias
pip install matplotlib seaborn plotly

# Verificar configuración X11 (Linux)
export DISPLAY=:0
```

#### 2. WebSocket desconexiones
```python
# Implementar reconexión automática
async def reconnect_websocket():
    while True:
        try:
            await websocket.connect()
            break
        except:
            await asyncio.sleep(5)
```

#### 3. Memoria alta con gráficos
```python
# Limpiar figuras después de uso
plt.close(fig)

# Usar formato vectorial para gráficos grandes
config.export_format = "svg"
```

## Futuras Mejoras

### Roadmap
- [ ] Soporte para múltiples idiomas
- [ ] Exportación a PowerBI/Tableau
- [ ] Alertas por email/SMS
- [ ] Dashboard móvil nativo
- [ ] Machine Learning para predicciones
- [ ] Integración con mapas reales (OpenStreetMap)
- [ ] Reportes programados automáticos
- [ ] Cache distribuido con Redis

### Contribuciones
- Documentar nuevas funcionalidades
- Mantener cobertura de tests > 90%
- Seguir estándares de código Python (PEP 8)
- Actualizar documentación con cambios

---

*Para más información, consultar la documentación de la API en `/docs` cuando el servidor esté ejecutándose.*
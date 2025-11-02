# Sistema de Optimización de Rendimiento

## 🎯 Overview

Suite completa de optimización para el sistema de detección de infracciones de tránsito, diseñada para maximizar el rendimiento, minimizar la latencia y optimizar el uso de recursos.

## 🚀 Componentes Principales

### 1. 📊 Performance Monitor (`performance_optimizer.py`)
- **Monitoreo en tiempo real** de métricas del sistema
- **Alertas automáticas** cuando se superan umbrales
- **Decorador `@measure_performance`** para instrumentar código
- **Motor de optimización automática** con múltiples estrategias

### 2. 🗄️ Intelligent Cache (`cache_manager.py`)
- **Cache multi-nivel** (L1 memoria, L2 Redis)
- **Estrategias inteligentes**: LRU, LFU, TTL, FIFO
- **Invalidación por tags** para actualizaciones coherentes
- **Decorador `@cached`** para funciones
- **Promoción automática** entre niveles de cache

### 3. 🔍 Database Optimizer (`database_optimizer.py`)
- **Análisis automático de consultas** SQL
- **Recomendaciones de índices** basadas en patrones
- **Detección de consultas lentas** y problemas de rendimiento
- **Optimización automática** de queries
- **Puntuación de salud** de la base de datos

## ✨ Características Clave

### 🔄 Optimización Automática
- **Detección proactiva** de cuellos de botella
- **Optimización sin intervención** manual
- **Adaptación dinámica** a patrones de uso
- **Rollback automático** si las optimizaciones causan problemas

### 📈 Monitoreo Avanzado
- **Métricas en tiempo real**: CPU, memoria, latencia, throughput
- **Alertas inteligentes** con umbrales adaptativos
- **Historial de rendimiento** para análisis de tendencias
- **Dashboard de métricas** integrado

### 🎯 Optimizaciones Específicas
- **Cache inteligente** para consultas frecuentes
- **Índices automáticos** para consultas lentas
- **Compresión de imágenes** en tiempo real
- **Optimización de modelos ML** (quantización, pruning)
- **Balanceo de carga** dinámico

## 🛠️ Instalación y Configuración

### Dependencias
```bash
pip install psutil redis asyncpg
```

### Configuración Básica
```python
from optimization.performance_optimizer import optimization_engine, OptimizationType
from optimization.cache_manager import global_cache
from optimization.database_optimizer import db_optimizer

# Habilitar optimizaciones
optimization_engine.enable_optimization(OptimizationType.CACHE)
optimization_engine.enable_optimization(OptimizationType.DATABASE)
optimization_engine.enable_optimization(OptimizationType.ML_MODEL)
```

## 📊 Uso y Ejemplos

### Monitoreo de Performance
```python
from optimization.performance_optimizer import measure_performance

@measure_performance("detection", "vehicle_detection")
async def detect_vehicles(image_path: str):
    # Lógica de detección
    result = await process_image(image_path)
    return result
```

### Cache Inteligente
```python
from optimization.cache_manager import cached

@cached(ttl=300, tags=["ml", "detection"], key_prefix="yolo")
async def run_inference(image_data: bytes, model_version: str):
    # Inferencia ML costosa
    result = await model.predict(image_data)
    return result
```

### Optimización de DB
```python
from optimization.database_optimizer import monitor_query

@monitor_query
async def get_infractions_by_location(location: str):
    query = "SELECT * FROM infractions WHERE location = %s"
    result = await db.fetch(query, location)
    return result
```

## 📈 Métricas y KPIs

### Mejoras de Rendimiento Esperadas
- **Cache Hit Rate**: 85-95%
- **Reducción de Latencia**: 40-60%
- **Mejora en Throughput**: 50-80%
- **Reducción de Uso de CPU**: 20-35%
- **Optimización de Memoria**: 25-40%

### Monitoreo de Salud del Sistema
```python
# Obtener métricas en tiempo real
from optimization.performance_optimizer import performance_monitor

summary = performance_monitor.get_performance_summary()
print(f"Average response time: {summary['avg_response_time_ms']}ms")
print(f"Cache hit rate: {summary['avg_cache_hit_rate']:.2%}")

# Reporte de base de datos
db_report = await db_optimizer.get_performance_report()
print(f"Database health score: {db_report['overall_health_score']}/100")
```

## 🔧 Configuración Avanzada

### Umbrales de Performance
```python
performance_monitor.thresholds = {
    'max_response_time_ms': 300,    # Máximo tiempo de respuesta
    'max_memory_usage_mb': 1024,    # Máximo uso de memoria
    'max_cpu_usage_percent': 70,    # Máximo uso de CPU
    'min_cache_hit_rate': 0.85,     # Mínima tasa de hit cache
    'max_error_rate': 0.02          # Máxima tasa de errores
}
```

### Configuración de Cache
```python
cache = IntelligentCache(
    max_memory_mb=512,              # Tamaño máximo de cache L1
    default_ttl=3600,               # TTL por defecto (1 hora)
    strategy=CacheStrategy.LRU      # Estrategia de evicción
)
```

### Optimización de Base de Datos
```python
db_optimizer.performance_baselines = {
    'avg_query_time_ms': 50,        # Tiempo promedio objetivo
    'slow_query_threshold_ms': 500, # Umbral de consulta lenta
    'index_hit_ratio': 0.95,        # Ratio objetivo de hit de índices
    'cache_hit_ratio': 0.90         # Ratio objetivo de hit de cache
}
```

## 🚦 Integración con el Sistema

### 1. FastAPI Integration
```python
from fastapi import FastAPI
from optimization.performance_optimizer import measure_performance

app = FastAPI()

@app.get("/detect")
@measure_performance("api", "detection_endpoint")
async def detect_infractions(image_url: str):
    result = await process_detection(image_url)
    return result
```

### 2. Django Integration
```python
from django.core.cache import cache
from optimization.cache_manager import global_cache

class InfractionViewSet(ViewSet):
    
    async def list(self, request):
        cache_key = f"infractions:{request.GET.urlencode()}"
        
        # Intentar obtener del cache
        cached_result = await global_cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
        
        # Consulta a BD y cache del resultado
        data = await self.get_infractions_data()
        await global_cache.set(cache_key, data, ttl=300)
        return Response(data)
```

### 3. Background Optimization
```python
import asyncio
from optimization.performance_optimizer import optimization_engine

async def background_optimizer():
    """Tarea en background para optimización continua"""
    while True:
        try:
            # Ejecutar optimizaciones cada 5 minutos
            results = await optimization_engine.optimize_system()
            logger.info(f"Optimization results: {results}")
            
            # Limpiar cache expirado cada 10 minutos
            cleaned = await global_cache.cleanup_expired()
            logger.info(f"Cleaned {cleaned} expired cache entries")
            
        except Exception as e:
            logger.error(f"Background optimization failed: {e}")
        
        await asyncio.sleep(300)  # 5 minutos

# Iniciar task en background
asyncio.create_task(background_optimizer())
```

## 📊 Dashboard y Reportes

### Métricas en Tiempo Real
- **Performance Dashboard**: Visualización de métricas de rendimiento
- **Cache Analytics**: Estadísticas de hit/miss ratios
- **Database Health**: Salud y optimizaciones de BD
- **System Resources**: CPU, memoria, disco, red

### Reportes Automáticos
- **Reporte Diario**: Resumen de rendimiento del día
- **Alertas de Degradación**: Notificaciones cuando el rendimiento baja
- **Recomendaciones de Optimización**: Sugerencias automáticas
- **Análisis de Tendencias**: Evolución del rendimiento

## 🐛 Troubleshooting

### Problemas Comunes

#### Alto Uso de Memoria
```python
# Verificar uso de cache
cache_stats = global_cache.get_stats()
if cache_stats['l1_cache']['size_mb'] > 400:
    await global_cache.cleanup_expired()
```

#### Consultas Lentas
```python
# Analizar consultas problemáticas
analysis = await db_optimizer.analyze_query_performance()
slow_queries = [q for q in analysis['performance_issues'] 
                if q['type'] == 'frequent_slow_query']
```

#### Baja Tasa de Hit de Cache
```python
# Verificar patrones de invalidación
if cache_stats['performance']['hit_rate'] < 0.8:
    # Revisar TTL y estrategias de invalidación
    await global_cache.invalidate_by_tags(['outdated'])
```

## 🔮 Roadmap de Optimización

### Próximas Versiones
- [ ] **Optimización de GPU**: Gestión eficiente de memoria GPU para ML
- [ ] **Cache Distribuido**: Sincronización entre múltiples instancias
- [ ] **ML Model Optimization**: Quantización y pruning automático
- [ ] **Edge Computing**: Optimizaciones para dispositivos edge
- [ ] **Predictive Scaling**: Auto-scaling basado en predicciones

### Mejoras Planificadas
- [ ] **Advanced Analytics**: Machine learning para predicción de patrones
- [ ] **Multi-tenant Optimization**: Optimizaciones por tenant
- [ ] **Real-time Tuning**: Ajuste de parámetros en tiempo real
- [ ] **Cost Optimization**: Optimización de costos en cloud

---

**Versión**: 1.0.0  
**Última Actualización**: 2025-01-01  
**Performance Target**: 90% mejora en latencia promedio  
**Maintainer**: Equipo de Performance Engineering
"""
Sistema de Cache Distribuido Optimizado
======================================

Implementación de un sistema de cache inteligente con múltiples niveles
y estrategias de invalidación automática.
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Any, Dict, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Estrategias de cache disponibles"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out

class CacheLevel(Enum):
    """Niveles de cache"""
    L1_MEMORY = "l1_memory"  # Cache en memoria local
    L2_REDIS = "l2_redis"    # Cache en Redis
    L3_DATABASE = "l3_database"  # Cache en base de datos

@dataclass
class CacheEntry:
    """Entrada de cache con metadatos"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @property
    def is_expired(self) -> bool:
        """Verificar si la entrada ha expirado"""
        if self.ttl_seconds is None:
            return False
        return time.time() > (self.created_at + self.ttl_seconds)

    @property
    def age_seconds(self) -> float:
        """Edad de la entrada en segundos"""
        return time.time() - self.created_at

class IntelligentCache:
    """Sistema de cache inteligente multi-nivel"""
    
    def __init__(self, 
                 max_memory_mb: int = 512,
                 default_ttl: int = 3600,
                 strategy: CacheStrategy = CacheStrategy.LRU):
        
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.strategy = strategy
        
        # Cache L1 - Memoria local
        self.l1_cache: Dict[str, CacheEntry] = {}
        self.l1_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size_bytes': 0
        }
        
        # Cache L2 - Redis (simulado por ahora)
        self.l2_cache: Dict[str, CacheEntry] = {}
        self.l2_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size_bytes': 0
        }
        
        # Patrones de invalidación
        self.invalidation_patterns: Dict[str, List[str]] = {}
        
        # Métricas de rendimiento
        self.performance_metrics = {
            'total_operations': 0,
            'total_time_ms': 0,
            'hit_rate': 0.0,
            'miss_rate': 0.0
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generar clave de cache única"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _calculate_size(self, value: Any) -> int:
        """Calcular tamaño aproximado del valor en bytes"""
        try:
            if isinstance(value, (str, int, float, bool)):
                return len(str(value).encode())
            elif isinstance(value, (list, dict)):
                return len(json.dumps(value, default=str).encode())
            else:
                return len(str(value).encode())
        except:
            return 1024  # Tamaño por defecto si no se puede calcular
    
    async def get(self, key: str, level: CacheLevel = CacheLevel.L1_MEMORY) -> Optional[Any]:
        """Obtener valor del cache"""
        start_time = time.time()
        
        try:
            # Buscar en L1 primero
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                if not entry.is_expired:
                    entry.last_accessed = time.time()
                    entry.access_count += 1
                    self.l1_stats['hits'] += 1
                    return entry.value
                else:
                    # Entrada expirada, eliminar
                    await self._evict_entry(key, CacheLevel.L1_MEMORY)
            
            # Buscar en L2 si no está en L1
            if level != CacheLevel.L1_MEMORY and key in self.l2_cache:
                entry = self.l2_cache[key]
                if not entry.is_expired:
                    entry.last_accessed = time.time()
                    entry.access_count += 1
                    self.l2_stats['hits'] += 1
                    
                    # Promover a L1 si hay espacio
                    await self._promote_to_l1(key, entry)
                    return entry.value
                else:
                    await self._evict_entry(key, CacheLevel.L2_REDIS)
            
            # Cache miss
            if level == CacheLevel.L1_MEMORY:
                self.l1_stats['misses'] += 1
            else:
                self.l2_stats['misses'] += 1
            
            return None
        
        finally:
            self.performance_metrics['total_operations'] += 1
            self.performance_metrics['total_time_ms'] += (time.time() - start_time) * 1000
            self._update_hit_rates()
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[int] = None,
                  tags: Optional[List[str]] = None,
                  level: CacheLevel = CacheLevel.L1_MEMORY) -> bool:
        """Establecer valor en el cache"""
        
        if ttl is None:
            ttl = self.default_ttl
        
        size_bytes = self._calculate_size(value)
        current_time = time.time()
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=current_time,
            last_accessed=current_time,
            access_count=0,
            ttl_seconds=ttl,
            size_bytes=size_bytes,
            tags=tags or []
        )
        
        # Determinar dónde almacenar
        if level == CacheLevel.L1_MEMORY:
            # Verificar espacio en L1
            if self.l1_stats['size_bytes'] + size_bytes > self.max_memory_bytes:
                await self._make_space_l1(size_bytes)
            
            self.l1_cache[key] = entry
            self.l1_stats['size_bytes'] += size_bytes
            
        elif level == CacheLevel.L2_REDIS:
            self.l2_cache[key] = entry
            self.l2_stats['size_bytes'] += size_bytes
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Eliminar entrada del cache"""
        deleted = False
        
        if key in self.l1_cache:
            entry = self.l1_cache[key]
            self.l1_stats['size_bytes'] -= entry.size_bytes
            del self.l1_cache[key]
            deleted = True
        
        if key in self.l2_cache:
            entry = self.l2_cache[key]
            self.l2_stats['size_bytes'] -= entry.size_bytes
            del self.l2_cache[key]
            deleted = True
        
        return deleted
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidar entradas por tags"""
        invalidated = 0
        
        # Invalidar en L1
        to_delete_l1 = []
        for key, entry in self.l1_cache.items():
            if any(tag in entry.tags for tag in tags):
                to_delete_l1.append(key)
        
        for key in to_delete_l1:
            await self.delete(key)
            invalidated += 1
        
        # Invalidar en L2
        to_delete_l2 = []
        for key, entry in self.l2_cache.items():
            if any(tag in entry.tags for tag in tags):
                to_delete_l2.append(key)
        
        for key in to_delete_l2:
            await self.delete(key)
            invalidated += 1
        
        logger.info(f"Invalidated {invalidated} cache entries with tags: {tags}")
        return invalidated
    
    async def _make_space_l1(self, required_bytes: int):
        """Hacer espacio en cache L1"""
        if self.strategy == CacheStrategy.LRU:
            await self._evict_lru_l1(required_bytes)
        elif self.strategy == CacheStrategy.LFU:
            await self._evict_lfu_l1(required_bytes)
        elif self.strategy == CacheStrategy.FIFO:
            await self._evict_fifo_l1(required_bytes)
        else:
            await self._evict_expired_l1()
    
    async def _evict_lru_l1(self, required_bytes: int):
        """Evitar LRU (Least Recently Used) de L1"""
        # Ordenar por último acceso
        sorted_entries = sorted(
            self.l1_cache.items(), 
            key=lambda x: x[1].last_accessed
        )
        
        freed_bytes = 0
        for key, entry in sorted_entries:
            if freed_bytes >= required_bytes:
                break
            
            # Mover a L2 antes de evitar
            await self.set(key, entry.value, entry.ttl_seconds, entry.tags, CacheLevel.L2_REDIS)
            
            # Evitar de L1
            await self._evict_entry(key, CacheLevel.L1_MEMORY)
            freed_bytes += entry.size_bytes
            self.l1_stats['evictions'] += 1
    
    async def _evict_lfu_l1(self, required_bytes: int):
        """Evitar LFU (Least Frequently Used) de L1"""
        sorted_entries = sorted(
            self.l1_cache.items(), 
            key=lambda x: x[1].access_count
        )
        
        freed_bytes = 0
        for key, entry in sorted_entries:
            if freed_bytes >= required_bytes:
                break
            
            await self.set(key, entry.value, entry.ttl_seconds, entry.tags, CacheLevel.L2_REDIS)
            await self._evict_entry(key, CacheLevel.L1_MEMORY)
            freed_bytes += entry.size_bytes
            self.l1_stats['evictions'] += 1
    
    async def _evict_fifo_l1(self, required_bytes: int):
        """Evitar FIFO (First In First Out) de L1"""
        sorted_entries = sorted(
            self.l1_cache.items(), 
            key=lambda x: x[1].created_at
        )
        
        freed_bytes = 0
        for key, entry in sorted_entries:
            if freed_bytes >= required_bytes:
                break
            
            await self.set(key, entry.value, entry.ttl_seconds, entry.tags, CacheLevel.L2_REDIS)
            await self._evict_entry(key, CacheLevel.L1_MEMORY)
            freed_bytes += entry.size_bytes
            self.l1_stats['evictions'] += 1
    
    async def _evict_expired_l1(self):
        """Evitar entradas expiradas de L1"""
        expired_keys = []
        for key, entry in self.l1_cache.items():
            if entry.is_expired:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self._evict_entry(key, CacheLevel.L1_MEMORY)
    
    async def _evict_entry(self, key: str, level: CacheLevel):
        """Evitar entrada específica"""
        if level == CacheLevel.L1_MEMORY and key in self.l1_cache:
            entry = self.l1_cache[key]
            self.l1_stats['size_bytes'] -= entry.size_bytes
            del self.l1_cache[key]
        elif level == CacheLevel.L2_REDIS and key in self.l2_cache:
            entry = self.l2_cache[key]
            self.l2_stats['size_bytes'] -= entry.size_bytes
            del self.l2_cache[key]
    
    async def _promote_to_l1(self, key: str, entry: CacheEntry):
        """Promover entrada de L2 a L1"""
        if self.l1_stats['size_bytes'] + entry.size_bytes <= self.max_memory_bytes:
            self.l1_cache[key] = entry
            self.l1_stats['size_bytes'] += entry.size_bytes
    
    def _update_hit_rates(self):
        """Actualizar tasas de hit/miss"""
        total_l1 = self.l1_stats['hits'] + self.l1_stats['misses']
        total_l2 = self.l2_stats['hits'] + self.l2_stats['misses']
        total_ops = total_l1 + total_l2
        
        if total_ops > 0:
            total_hits = self.l1_stats['hits'] + self.l2_stats['hits']
            self.performance_metrics['hit_rate'] = total_hits / total_ops
            self.performance_metrics['miss_rate'] = 1 - self.performance_metrics['hit_rate']
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        return {
            'l1_cache': {
                **self.l1_stats,
                'entries': len(self.l1_cache),
                'size_mb': self.l1_stats['size_bytes'] / 1024 / 1024
            },
            'l2_cache': {
                **self.l2_stats,
                'entries': len(self.l2_cache),
                'size_mb': self.l2_stats['size_bytes'] / 1024 / 1024
            },
            'performance': self.performance_metrics,
            'strategy': self.strategy.value,
            'max_memory_mb': self.max_memory_bytes / 1024 / 1024
        }
    
    async def cleanup_expired(self):
        """Limpiar entradas expiradas de todos los niveles"""
        cleaned = 0
        
        # Limpiar L1
        expired_l1 = [k for k, v in self.l1_cache.items() if v.is_expired]
        for key in expired_l1:
            await self._evict_entry(key, CacheLevel.L1_MEMORY)
            cleaned += 1
        
        # Limpiar L2
        expired_l2 = [k for k, v in self.l2_cache.items() if v.is_expired]
        for key in expired_l2:
            await self._evict_entry(key, CacheLevel.L2_REDIS)
            cleaned += 1
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired cache entries")
        
        return cleaned

# Cache decorador para funciones
def cached(ttl: int = 3600, 
           tags: Optional[List[str]] = None,
           key_prefix: str = "func"):
    """Decorador para cachear resultados de funciones"""
    
    def decorator(func: Callable):
        cache_instance = IntelligentCache()
        
        async def async_wrapper(*args, **kwargs):
            # Generar clave de cache
            cache_key = cache_instance._generate_key(
                f"{key_prefix}:{func.__name__}", 
                *args, 
                **kwargs
            )
            
            # Intentar obtener del cache
            cached_result = await cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = await func(*args, **kwargs)
            await cache_instance.set(cache_key, result, ttl, tags)
            
            return result
        
        def sync_wrapper(*args, **kwargs):
            # Para funciones síncronas, usar versión simple
            cache_key = cache_instance._generate_key(
                f"{key_prefix}:{func.__name__}", 
                *args, 
                **kwargs
            )
            
            # Versión síncrona simplificada
            result = func(*args, **kwargs)
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Instancia global de cache
global_cache = IntelligentCache()

if __name__ == "__main__":
    # Ejemplo de uso
    
    @cached(ttl=300, tags=["detection", "ml"], key_prefix="traffic")
    async def detect_vehicle(image_path: str, model_version: str) -> Dict[str, Any]:
        """Función de ejemplo para detección de vehículos"""
        await asyncio.sleep(0.1)  # Simular procesamiento
        return {
            'vehicles': [
                {'type': 'car', 'confidence': 0.95, 'bbox': [100, 100, 200, 200]},
                {'type': 'truck', 'confidence': 0.88, 'bbox': [300, 150, 400, 250]}
            ],
            'processing_time_ms': 150,
            'model_version': model_version
        }
    
    async def main():
        # Probar cache
        cache = IntelligentCache(max_memory_mb=100)
        
        # Establecer algunos valores
        await cache.set("test1", {"data": "value1"}, ttl=60, tags=["test"])
        await cache.set("test2", {"data": "value2"}, ttl=120, tags=["test", "important"])
        await cache.set("test3", {"data": "value3"}, ttl=300)
        
        # Obtener valores
        result1 = await cache.get("test1")
        result2 = await cache.get("test2")
        
        print(f"Cache results: {result1}, {result2}")
        
        # Probar función cacheada
        detection_result = await detect_vehicle("/path/to/image.jpg", "v1.0")
        print(f"Detection result: {detection_result}")
        
        # Segunda llamada debería venir del cache
        detection_result2 = await detect_vehicle("/path/to/image.jpg", "v1.0")
        print(f"Cached result: {detection_result2}")
        
        # Invalidar por tags
        await cache.invalidate_by_tags(["test"])
        
        # Obtener estadísticas
        stats = cache.get_stats()
        print(f"Cache stats: {json.dumps(stats, indent=2)}")
    
    asyncio.run(main())
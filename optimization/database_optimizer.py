"""
Optimizador de Base de Datos
===========================

Sistema inteligente para optimizar consultas, índices y rendimiento 
de la base de datos PostgreSQL del sistema de infracciones.
"""

import asyncio
import logging
import time
import psutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Tipos de consultas SQL"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    AGGREGATION = "AGGREGATION"
    JOIN = "JOIN"

@dataclass
class QueryAnalysis:
    """Análisis de una consulta SQL"""
    query_id: str
    query_text: str
    query_type: QueryType
    execution_time_ms: float
    rows_examined: int
    rows_returned: int
    index_usage: Dict[str, bool]
    cost_estimate: float
    frequency: int = 1
    optimization_suggestions: List[str] = None

    def __post_init__(self):
        if self.optimization_suggestions is None:
            self.optimization_suggestions = []

@dataclass
class IndexSuggestion:
    """Sugerencia de índice"""
    table_name: str
    columns: List[str]
    index_type: str  # btree, hash, gin, gist
    estimated_improvement: float
    creation_cost: float
    maintenance_cost: float
    usage_frequency: int

class DatabaseOptimizer:
    """Optimizador inteligente de base de datos"""
    
    def __init__(self, connection_pool=None):
        self.connection_pool = connection_pool
        self.query_history: Dict[str, QueryAnalysis] = {}
        self.index_suggestions: List[IndexSuggestion] = []
        self.performance_baselines = {
            'avg_query_time_ms': 0,
            'slow_query_threshold_ms': 1000,
            'index_hit_ratio': 0.95,
            'cache_hit_ratio': 0.90
        }
        
        # Patrones de consultas comunes del sistema
        self.query_patterns = {
            'infraction_by_plate': {
                'pattern': 'SELECT * FROM infractions WHERE vehicle_plate = %s',
                'frequency': 'high',
                'suggested_index': ['vehicle_plate']
            },
            'infraction_by_location_time': {
                'pattern': 'SELECT * FROM infractions WHERE location = %s AND timestamp BETWEEN %s AND %s',
                'frequency': 'high',
                'suggested_index': ['location', 'timestamp']
            },
            'camera_status': {
                'pattern': 'SELECT * FROM devices WHERE status = %s AND last_seen > %s',
                'frequency': 'medium',
                'suggested_index': ['status', 'last_seen']
            },
            'analytics_daily': {
                'pattern': 'SELECT DATE(timestamp), COUNT(*) FROM infractions GROUP BY DATE(timestamp)',
                'frequency': 'medium',
                'suggested_index': ['timestamp']
            }
        }
    
    async def analyze_query_performance(self) -> Dict[str, Any]:
        """Analizar rendimiento general de consultas"""
        
        # Simular análisis de consultas (en producción usaría pg_stat_statements)
        analysis_results = {
            'total_queries_analyzed': len(self.query_history),
            'avg_execution_time_ms': 0,
            'slow_queries_count': 0,
            'most_frequent_queries': [],
            'index_recommendations': [],
            'performance_issues': []
        }
        
        if not self.query_history:
            return analysis_results
        
        # Calcular métricas promedio
        total_time = sum(q.execution_time_ms for q in self.query_history.values())
        analysis_results['avg_execution_time_ms'] = total_time / len(self.query_history)
        
        # Identificar consultas lentas
        slow_queries = [
            q for q in self.query_history.values() 
            if q.execution_time_ms > self.performance_baselines['slow_query_threshold_ms']
        ]
        analysis_results['slow_queries_count'] = len(slow_queries)
        
        # Consultas más frecuentes
        frequent_queries = sorted(
            self.query_history.values(), 
            key=lambda x: x.frequency, 
            reverse=True
        )[:10]
        
        analysis_results['most_frequent_queries'] = [
            {
                'query_id': q.query_id,
                'frequency': q.frequency,
                'avg_time_ms': q.execution_time_ms,
                'type': q.query_type.value
            }
            for q in frequent_queries
        ]
        
        # Generar recomendaciones de índices
        index_recommendations = await self._generate_index_recommendations()
        analysis_results['index_recommendations'] = [
            {
                'table': idx.table_name,
                'columns': idx.columns,
                'type': idx.index_type,
                'estimated_improvement': idx.estimated_improvement,
                'priority': 'high' if idx.estimated_improvement > 0.3 else 'medium'
            }
            for idx in index_recommendations[:5]  # Top 5 recomendaciones
        ]
        
        # Identificar problemas de rendimiento
        performance_issues = await self._identify_performance_issues()
        analysis_results['performance_issues'] = performance_issues
        
        return analysis_results
    
    async def _generate_index_recommendations(self) -> List[IndexSuggestion]:
        """Generar recomendaciones de índices basadas en patrones de consulta"""
        
        recommendations = []
        
        # Recomendaciones basadas en patrones conocidos
        pattern_recommendations = [
            IndexSuggestion(
                table_name="infractions",
                columns=["vehicle_plate"],
                index_type="btree",
                estimated_improvement=0.6,
                creation_cost=0.2,
                maintenance_cost=0.1,
                usage_frequency=100
            ),
            IndexSuggestion(
                table_name="infractions", 
                columns=["location", "timestamp"],
                index_type="btree",
                estimated_improvement=0.4,
                creation_cost=0.3,
                maintenance_cost=0.15,
                usage_frequency=80
            ),
            IndexSuggestion(
                table_name="infractions",
                columns=["timestamp"],
                index_type="btree", 
                estimated_improvement=0.5,
                creation_cost=0.15,
                maintenance_cost=0.08,
                usage_frequency=90
            ),
            IndexSuggestion(
                table_name="devices",
                columns=["status", "last_seen"],
                index_type="btree",
                estimated_improvement=0.3,
                creation_cost=0.1,
                maintenance_cost=0.05,
                usage_frequency=60
            ),
            IndexSuggestion(
                table_name="vehicles",
                columns=["plate"],
                index_type="btree",
                estimated_improvement=0.7,
                creation_cost=0.15,
                maintenance_cost=0.08,
                usage_frequency=120
            )
        ]
        
        recommendations.extend(pattern_recommendations)
        
        # Ordenar por impacto estimado
        recommendations.sort(key=lambda x: x.estimated_improvement, reverse=True)
        
        return recommendations
    
    async def _identify_performance_issues(self) -> List[Dict[str, Any]]:
        """Identificar problemas específicos de rendimiento"""
        
        issues = []
        
        # Verificar consultas sin índices
        for query in self.query_history.values():
            if not any(query.index_usage.values()):
                issues.append({
                    'type': 'missing_index',
                    'severity': 'high',
                    'description': f'Query {query.query_id} not using any indexes',
                    'suggestion': 'Add appropriate indexes for this query pattern',
                    'query_id': query.query_id
                })
        
        # Verificar consultas con alta proporción de filas examinadas vs retornadas
        for query in self.query_history.values():
            if query.rows_returned > 0 and query.rows_examined / query.rows_returned > 100:
                issues.append({
                    'type': 'inefficient_scan',
                    'severity': 'medium',
                    'description': f'Query {query.query_id} examining too many rows',
                    'suggestion': 'Optimize WHERE conditions or add selective indexes',
                    'query_id': query.query_id,
                    'efficiency_ratio': query.rows_examined / query.rows_returned
                })
        
        # Verificar consultas frecuentes y lentas
        for query in self.query_history.values():
            if (query.frequency > 10 and 
                query.execution_time_ms > self.performance_baselines['slow_query_threshold_ms']):
                issues.append({
                    'type': 'frequent_slow_query',
                    'severity': 'critical',
                    'description': f'Frequently executed slow query: {query.query_id}',
                    'suggestion': 'Optimize this query as it has high impact',
                    'query_id': query.query_id,
                    'frequency': query.frequency,
                    'avg_time_ms': query.execution_time_ms
                })
        
        return issues
    
    async def optimize_queries(self) -> Dict[str, Any]:
        """Ejecutar optimizaciones automáticas de consultas"""
        
        optimization_results = {
            'indexes_created': 0,
            'queries_optimized': 0,
            'estimated_improvement': 0,
            'actions_taken': []
        }
        
        # Crear índices recomendados automáticamente
        recommendations = await self._generate_index_recommendations()
        high_priority_indexes = [
            idx for idx in recommendations 
            if idx.estimated_improvement > 0.4
        ]
        
        for index_rec in high_priority_indexes:
            success = await self._create_index(index_rec)
            if success:
                optimization_results['indexes_created'] += 1
                optimization_results['actions_taken'].append(
                    f"Created index on {index_rec.table_name}({', '.join(index_rec.columns)})"
                )
        
        # Actualizar estadísticas de tablas
        updated_stats = await self._update_table_statistics()
        optimization_results['actions_taken'].extend(updated_stats)
        
        # Limpiar consultas obsoletas del plan cache
        cleaned_cache = await self._clean_query_cache()
        optimization_results['actions_taken'].append(f"Cleaned {cleaned_cache} cached query plans")
        
        # Calcular mejora estimada total
        total_improvement = sum(
            idx.estimated_improvement for idx in high_priority_indexes
        )
        optimization_results['estimated_improvement'] = min(total_improvement, 0.8)  # Max 80%
        
        optimization_results['queries_optimized'] = len(high_priority_indexes)
        
        return optimization_results
    
    async def _create_index(self, index_rec: IndexSuggestion) -> bool:
        """Crear índice en la base de datos (simulado)"""
        
        index_name = f"idx_{index_rec.table_name}_{'_'.join(index_rec.columns)}"
        
        # Simular creación de índice
        logger.info(f"Creating index: {index_name}")
        await asyncio.sleep(0.1)  # Simular tiempo de creación
        
        # En producción, ejecutaría:
        # CREATE INDEX CONCURRENTLY idx_name ON table_name (columns)
        
        return True
    
    async def _update_table_statistics(self) -> List[str]:
        """Actualizar estadísticas de tablas"""
        
        tables = ['infractions', 'vehicles', 'devices', 'users']
        actions = []
        
        for table in tables:
            # Simular actualización de estadísticas
            logger.info(f"Updating statistics for table: {table}")
            await asyncio.sleep(0.05)
            actions.append(f"Updated statistics for table {table}")
        
        return actions
    
    async def _clean_query_cache(self) -> int:
        """Limpiar cache de planes de consulta"""
        
        # Simular limpieza de cache
        await asyncio.sleep(0.1)
        cleaned_plans = 25  # Número simulado
        
        logger.info(f"Cleaned {cleaned_plans} query plans from cache")
        return cleaned_plans
    
    def record_query(self, 
                     query_text: str, 
                     execution_time_ms: float,
                     rows_examined: int = 0,
                     rows_returned: int = 0) -> str:
        """Registrar una consulta para análisis"""
        
        # Generar ID único para la consulta
        import hashlib
        query_id = hashlib.md5(query_text.encode()).hexdigest()[:8]
        
        # Determinar tipo de consulta
        query_type = QueryType.SELECT
        query_upper = query_text.upper().strip()
        
        if query_upper.startswith('INSERT'):
            query_type = QueryType.INSERT
        elif query_upper.startswith('UPDATE'):
            query_type = QueryType.UPDATE
        elif query_upper.startswith('DELETE'):
            query_type = QueryType.DELETE
        elif 'GROUP BY' in query_upper or 'COUNT(' in query_upper:
            query_type = QueryType.AGGREGATION
        elif 'JOIN' in query_upper:
            query_type = QueryType.JOIN
        
        # Actualizar o crear análisis de consulta
        if query_id in self.query_history:
            existing = self.query_history[query_id]
            existing.frequency += 1
            # Calcular promedio móvil del tiempo de ejecución
            existing.execution_time_ms = (
                (existing.execution_time_ms * (existing.frequency - 1) + execution_time_ms) 
                / existing.frequency
            )
        else:
            self.query_history[query_id] = QueryAnalysis(
                query_id=query_id,
                query_text=query_text,
                query_type=query_type,
                execution_time_ms=execution_time_ms,
                rows_examined=rows_examined,
                rows_returned=rows_returned,
                index_usage={},  # Se llenaría con análisis real
                cost_estimate=execution_time_ms * 0.1  # Estimación simple
            )
        
        return query_id
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generar reporte completo de rendimiento"""
        
        analysis = await self.analyze_query_performance()
        
        # Calcular métricas adicionales
        current_time = time.time()
        
        # Simular métricas del sistema de base de datos
        db_metrics = {
            'connection_count': 25,
            'active_connections': 8,
            'cache_hit_ratio': 0.92,
            'index_hit_ratio': 0.88,
            'total_db_size_mb': 2048,
            'largest_tables': [
                {'name': 'infractions', 'size_mb': 512, 'row_count': 150000},
                {'name': 'vehicles', 'size_mb': 128, 'row_count': 50000},
                {'name': 'devices', 'size_mb': 32, 'row_count': 100}
            ]
        }
        
        return {
            'timestamp': current_time,
            'query_analysis': analysis,
            'database_metrics': db_metrics,
            'optimization_opportunities': len(analysis['index_recommendations']),
            'critical_issues': len([
                issue for issue in analysis['performance_issues'] 
                if issue.get('severity') == 'critical'
            ]),
            'overall_health_score': self._calculate_health_score(analysis, db_metrics)
        }
    
    def _calculate_health_score(self, analysis: Dict, db_metrics: Dict) -> float:
        """Calcular puntuación de salud de la base de datos (0-100)"""
        
        score = 100
        
        # Penalizar por consultas lentas
        if analysis['slow_queries_count'] > 0:
            score -= min(analysis['slow_queries_count'] * 5, 30)
        
        # Penalizar por problemas críticos
        critical_issues = len([
            issue for issue in analysis['performance_issues'] 
            if issue.get('severity') == 'critical'
        ])
        score -= critical_issues * 10
        
        # Bonificar por buena tasa de hit de cache
        if db_metrics['cache_hit_ratio'] > 0.9:
            score += 5
        
        # Bonificar por buena tasa de hit de índices
        if db_metrics['index_hit_ratio'] > 0.85:
            score += 5
        
        return max(0, min(100, score))

# Instancia global del optimizador
db_optimizer = DatabaseOptimizer()

# Decorador para medir rendimiento de consultas
def monitor_query(func):
    """Decorador para monitorear consultas SQL"""
    
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            # Simular extracción de información de la consulta
            query_text = kwargs.get('query', 'UNKNOWN')
            execution_time = (time.time() - start_time) * 1000
            
            # Registrar la consulta
            db_optimizer.record_query(query_text, execution_time)
            
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            query_text = kwargs.get('query', 'UNKNOWN')
            execution_time = (time.time() - start_time) * 1000
            
            db_optimizer.record_query(query_text, execution_time)
            
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

if __name__ == "__main__":
    # Ejemplo de uso
    
    @monitor_query
    async def get_infractions_by_plate(plate: str):
        """Función de ejemplo que ejecuta consulta"""
        query = f"SELECT * FROM infractions WHERE vehicle_plate = '{plate}'"
        await asyncio.sleep(0.05)  # Simular ejecución
        return [{'id': 1, 'plate': plate, 'type': 'speeding'}]
    
    async def main():
        optimizer = DatabaseOptimizer()
        
        # Simular algunas consultas
        queries = [
            ("SELECT * FROM infractions WHERE vehicle_plate = 'ABC123'", 45),
            ("SELECT * FROM infractions WHERE location = 'Av. Javier Prado'", 120),
            ("SELECT COUNT(*) FROM infractions GROUP BY DATE(timestamp)", 200),
            ("SELECT * FROM devices WHERE status = 'active'", 30),
            ("SELECT * FROM infractions WHERE timestamp > '2024-01-01'", 1500),  # Consulta lenta
        ]
        
        for query_text, exec_time in queries:
            optimizer.record_query(query_text, exec_time, 1000, 50)
        
        # Analizar rendimiento
        analysis = await optimizer.analyze_query_performance()
        print("Query Performance Analysis:")
        print(json.dumps(analysis, indent=2))
        
        # Ejecutar optimizaciones
        optimization_results = await optimizer.optimize_queries()
        print("\nOptimization Results:")
        print(json.dumps(optimization_results, indent=2))
        
        # Generar reporte
        report = await optimizer.get_performance_report()
        print(f"\nOverall Health Score: {report['overall_health_score']}/100")
        
        # Probar función monitoreada
        result = await get_infractions_by_plate("XYZ789")
        print(f"\nQuery result: {result}")
    
    asyncio.run(main())
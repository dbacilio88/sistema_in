'use client';

import { useState, useEffect } from 'react';
import { 
  CameraIcon, 
  ExclamationTriangleIcon, 
  ClockIcon, 
  TruckIcon 
} from '@heroicons/react/24/outline';
import { apiService } from '@/services/api';

interface MetricCardProps {
  title: string;
  value: string | number;
  change: string;
  changeType: 'increase' | 'decrease';
  icon: React.ComponentType<any>;
}

function MetricCard({ title, value, change, changeType, icon: Icon }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <Icon className="h-8 w-8 text-blue-600" />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900">{value}</div>
              <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                changeType === 'increase' ? 'text-green-600' : 'text-red-600'
              }`}>
                {change}
              </div>
            </dd>
          </dl>
        </div>
      </div>
    </div>
  );
}

export function RealtimeMetrics() {
  const [metrics, setMetrics] = useState({
    activeCameras: 0,
    totalInfractions: 0,
    avgProcessingTime: 0,
    activeVehicles: 0
  });
  const [loading, setLoading] = useState(true);

  // Cargar datos reales desde la API
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const [stats, devicesData] = await Promise.all([
          apiService.getInfractionStats(),
          apiService.getDevices()
        ]);
        
        setMetrics({
          activeCameras: devicesData.results.filter((d: any) => d.status === 'active').length,
          totalInfractions: stats.today || 0,
          avgProcessingTime: 185, // Esto requeriría un endpoint específico
          activeVehicles: stats.total_infractions || 0
        });
        setLoading(false);
      } catch (error) {
        console.error('Error fetching metrics:', error);
        setLoading(false);
      }
    };

    fetchMetrics();

    // Actualizar cada 30 segundos
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard
        title="Cámaras Activas"
        value={metrics.activeCameras}
        change="+2.5%"
        changeType="increase"
        icon={CameraIcon}
      />
      <MetricCard
        title="Infracciones Hoy"
        value={metrics.totalInfractions}
        change="+12.3%"
        changeType="increase"
        icon={ExclamationTriangleIcon}
      />
      <MetricCard
        title="Tiempo Promedio (ms)"
        value={metrics.avgProcessingTime}
        change="-5.2%"
        changeType="decrease"
        icon={ClockIcon}
      />
      <MetricCard
        title="Vehículos Detectados"
        value={metrics.activeVehicles.toLocaleString()}
        change="+8.1%"
        changeType="increase"
        icon={TruckIcon}
      />
    </div>
  );
}
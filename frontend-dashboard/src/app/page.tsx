'use client';

import { useState, useEffect } from 'react';
import { RealtimeMetrics } from '@/components/RealtimeMetrics';
import { InfractionsTable } from '@/components/InfractionsTable';
import { TrafficMap } from '@/components/TrafficMap';
import { AnalyticsCharts } from '@/components/AnalyticsCharts';
import { DashboardHeader } from '@/components/DashboardHeader';
import { Sidebar } from '@/components/Sidebar';
import { Settings } from '@/components/Settings';
import { RealtimeMonitor } from '@/components/RealtimeMonitor';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Verificar conexión con el backend
    checkConnection();
    
    // Verificar conexión cada 30 segundos
    const interval = setInterval(() => {
      checkConnection();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/health/');
      setIsConnected(response.ok);
    } catch (error) {
      setIsConnected(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      {/* Contenido Principal */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <DashboardHeader isConnected={isConnected} />
        
        {/* Contenido */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <RealtimeMetrics />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <InfractionsTable />
                <TrafficMap />
              </div>
              <AnalyticsCharts />
            </div>
          )}
          
          {activeTab === 'infractions' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Gestión de Infracciones</h2>
              <InfractionsTable fullView={true} />
            </div>
          )}
          
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Análisis y Reportes</h2>
              <AnalyticsCharts fullView={true} />
            </div>
          )}
          
          {activeTab === 'map' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Mapa de Tráfico</h2>
              <TrafficMap fullView={true} />
            </div>
          )}
          
          {activeTab === 'realtime' && (
            <div className="space-y-6">
              <RealtimeMonitor />
            </div>
          )}
          
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <Settings />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

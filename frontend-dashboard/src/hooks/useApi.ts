'use client';

import { useState, useEffect } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

interface ApiHookResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useApi<T>(endpoint: string, options?: RequestInit): ApiHookResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [endpoint]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
}

// Hook específico para métricas en tiempo real
export function useMetrics() {
  return useApi<{
    activeCameras: number;
    totalInfractions: number;
    avgProcessingTime: number;
    activeVehicles: number;
    systemHealth: number;
  }>('/api/metrics');
}

// Hook específico para infracciones
export function useInfractions(limit?: number) {
  const endpoint = limit ? `/api/infractions?limit=${limit}` : '/api/infractions';
  return useApi<{
    infractions: Array<{
      id: string;
      type: string;
      vehiclePlate: string;
      location: string;
      timestamp: string;
      severity: 'high' | 'medium' | 'low';
      status: 'pending' | 'processed' | 'resolved';
    }>;
    total: number;
    page: number;
    totalPages: number;
  }>(endpoint);
}

// Hook específico para datos de analytics
export function useAnalytics(period: 'daily' | 'weekly' | 'monthly' = 'daily') {
  return useApi<{
    timeSeriesData: Array<{
      date: string;
      infracciones: number;
      procesamiento: number;
    }>;
    infractionTypes: Array<{
      name: string;
      value: number;
      color: string;
    }>;
    hourlyData: Array<{
      hour: number;
      count: number;
    }>;
    performanceMetrics: {
      precision: number;
      latency: number;
      uptime: number;
    };
  }>(`/api/analytics/${period}`);
}
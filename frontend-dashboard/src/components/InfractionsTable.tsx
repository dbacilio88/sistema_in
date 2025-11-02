'use client';

import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { EyeIcon, PhotoIcon } from '@heroicons/react/24/outline';
import { apiService, Infraction } from '@/services/api';

interface InfractionsTableProps {
  fullView?: boolean;
}

export function InfractionsTable({ fullView = false }: InfractionsTableProps) {
  const [infractions, setInfractions] = useState<Infraction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInfractions = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiService.getInfractions({ 
          limit: fullView ? 50 : 20 
        });
        setInfractions(data.results);
      } catch (err) {
        console.error('Error fetching infractions:', err);
        setError('Error al cargar las infracciones');
      } finally {
        setLoading(false);
      }
    };

    fetchInfractions();

    // Actualizar datos cada 30 segundos
    const interval = setInterval(fetchInfractions, 30000);
    return () => clearInterval(interval);
  }, [fullView]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-orange-100 text-orange-800';
      case 'processed': return 'bg-blue-100 text-blue-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-4 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-8">
        <div className="text-center text-red-600">
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  if (infractions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8">
        <div className="text-center text-gray-500">
          <p>No hay infracciones registradas</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">
          {fullView ? 'Todas las Infracciones' : 'Infracciones Recientes'}
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          {fullView ? 'Gestión completa de infracciones detectadas' : 'Últimas infracciones detectadas en tiempo real'}
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID / Placa
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ubicación
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fecha/Hora
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severidad
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {infractions.map((infraction) => (
              <tr key={infraction.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{infraction.infraction_code}</div>
                    <div className="text-sm text-gray-500">{infraction.license_plate_detected}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{infraction.infraction_type_display}</div>
                  {infraction.detected_speed && (
                    <div className="text-xs text-gray-500">
                      {infraction.detected_speed} km/h (límite: {infraction.speed_limit})
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{infraction.device_name}</div>
                  <div className="text-xs text-gray-500">{infraction.zone_name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {format(new Date(infraction.detected_at), 'dd/MM/yyyy', { locale: es })}
                  </div>
                  <div className="text-sm text-gray-500">
                    {format(new Date(infraction.detected_at), 'HH:mm:ss')}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(infraction.severity)}`}>
                    {infraction.severity_display}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(infraction.status)}`}>
                    {infraction.status_display}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    <button className="text-blue-600 hover:text-blue-900" title="Ver detalles">
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    <button className="text-gray-600 hover:text-gray-900" title="Ver evidencia">
                      <PhotoIcon className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {fullView && (
        <div className="px-6 py-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Mostrando {infractions.length} de {infractions.length} infracciones
            </div>
            <div className="flex space-x-2">
              <button className="px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                Anterior
              </button>
              <button className="px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                Siguiente
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
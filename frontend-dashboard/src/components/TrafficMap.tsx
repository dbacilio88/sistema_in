'use client';

import { useState, useEffect } from 'react';
import { MapIcon, CameraIcon } from '@heroicons/react/24/outline';
import { apiService, Device } from '@/services/api';

interface MapLocation {
  id: string;
  name: string;
  coordinates: [number, number];
  type: 'camera' | 'infraction';
  status: 'active' | 'inactive' | 'alert';
  count?: number;
  device_type?: string;
  zone?: string;
}

interface TrafficMapProps {
  fullView?: boolean;
}

export function TrafficMap({ fullView = false }: TrafficMapProps) {
  const [locations, setLocations] = useState<MapLocation[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<MapLocation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDevices();
    
    // Actualizar cada 30 segundos
    const interval = setInterval(() => {
      loadDevices();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const loadDevices = async () => {
    try {
      const response = await apiService.getDevices();
      
      if (response.results) {
        const deviceLocations: MapLocation[] = response.results
          .filter(device => device.location_lat && device.location_lon)
          .map(device => ({
            id: device.id,
            name: device.name,
            coordinates: [parseFloat(device.location_lon), parseFloat(device.location_lat)],
            type: 'camera' as const,
            status: device.status === 'online' ? 'active' as const : 'inactive' as const,
            device_type: device.device_type,
            zone: device.zone_name,
          }));
        
        setLocations(deviceLocations);
      }
    } catch (error) {
      console.error('Error al cargar dispositivos:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string, type: string) => {
    if (type === 'camera') {
      switch (status) {
        case 'active': return 'bg-green-500';
        case 'inactive': return 'bg-gray-400';
        default: return 'bg-yellow-500';
      }
    } else {
      return 'bg-red-500';
    }
  };

  const getStatusText = (status: string, type: string) => {
    if (type === 'camera') {
      switch (status) {
        case 'active': return 'Activa';
        case 'inactive': return 'Inactiva';
        default: return 'Alerta';
      }
    } else {
      return 'Infracción';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 flex items-center">
          <MapIcon className="h-5 w-5 mr-2" />
          {fullView ? 'Mapa de Tráfico Completo' : 'Mapa de Ubicaciones'}
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Ubicaciones de cámaras e infracciones en tiempo real
        </p>
      </div>

      <div className={`${fullView ? 'h-96' : 'h-64'} relative bg-gray-100 overflow-hidden`}>
        {/* Simulación del mapa */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-green-50">
          <div className="absolute inset-0 opacity-20">
            <svg viewBox="0 0 400 300" className="w-full h-full">
              {/* Calles principales simuladas */}
              <path d="M0,150 L400,150" stroke="#d1d5db" strokeWidth="3" />
              <path d="M200,0 L200,300" stroke="#d1d5db" strokeWidth="3" />
              <path d="M50,50 L350,250" stroke="#d1d5db" strokeWidth="2" />
              <path d="M50,250 L350,50" stroke="#d1d5db" strokeWidth="2" />
            </svg>
          </div>

          {/* Marcadores de ubicaciones */}
          {locations.map((location, index) => (
            <div
              key={location.id}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
              style={{
                left: `${20 + (index * 15) % 60}%`,
                top: `${30 + (index * 20) % 40}%`
              }}
              onClick={() => setSelectedLocation(location)}
            >
              <div className={`w-4 h-4 rounded-full ${getStatusColor(location.status, location.type)} border-2 border-white shadow-lg`}>
              </div>
              {location.type === 'camera' && (
                <CameraIcon className="w-3 h-3 text-white absolute top-0.5 left-0.5" />
              )}
              {location.count && (
                <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {location.count}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Panel de información */}
        {selectedLocation && (
          <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4 max-w-sm">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">{selectedLocation.name}</h4>
              <button 
                onClick={() => setSelectedLocation(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center">
                <span className={`w-2 h-2 rounded-full mr-2 ${getStatusColor(selectedLocation.status, selectedLocation.type)}`}></span>
                <span className="text-gray-600">
                  Estado: {getStatusText(selectedLocation.status, selectedLocation.type)}
                </span>
              </div>
              <div className="text-gray-600">
                Tipo: {selectedLocation.device_type || 'Cámara'}
              </div>
              {selectedLocation.zone && (
                <div className="text-gray-600">
                  Zona: {selectedLocation.zone}
                </div>
              )}
              {selectedLocation.count && (
                <div className="text-gray-600">
                  Detecciones hoy: {selectedLocation.count}
                </div>
              )}
              <div className="text-xs text-gray-500">
                Coordenadas: {selectedLocation.coordinates[1].toFixed(4)}, {selectedLocation.coordinates[0].toFixed(4)}
              </div>
            </div>
          </div>
        )}

        {/* Indicador de carga */}
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75">
            <div className="text-gray-600">Cargando ubicaciones...</div>
          </div>
        )}
      </div>

      {/* Leyenda */}
      <div className="px-6 py-4 border-t border-gray-200">
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span>Cámara Activa ({locations.filter(l => l.status === 'active').length})</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-gray-400 rounded-full mr-2"></div>
            <span>Cámara Inactiva ({locations.filter(l => l.status === 'inactive').length})</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
            <span>Infracción</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
            <span>Alerta</span>
          </div>
        </div>
      </div>
    </div>
  );
}
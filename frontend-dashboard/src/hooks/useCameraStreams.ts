import { useState, useEffect, useCallback } from 'react';
import { apiService, Device, Zone } from '@/services/api';

export interface CameraStream {
  deviceId: string;
  isStreaming: boolean;
  streamUrl: string;
}

export interface UseCameraStreamsReturn {
  zones: Zone[];
  devices: Device[];
  loading: boolean;
  error: string | null;
  activeStreams: CameraStream[];
  selectedDevices: string[];
  selectedZone: string;
  statusFilter: string;
  setSelectedZone: (zone: string) => void;
  setStatusFilter: (status: string) => void;
  setSelectedDevices: (devices: string[]) => void;
  toggleCameraStream: (deviceId: string) => void;
  startSelectedStreams: () => void;
  stopAllStreams: () => void;
  selectAllCameras: (devices: Device[]) => void;
  clearSelection: () => void;
  loadData: () => Promise<void>;
  filteredDevices: Device[];
  deviceStats: {
    total: number;
    active: number;
    streaming: number;
    selected: number;
  };
}

export function useCameraStreams(): UseCameraStreamsReturn {
  const [zones, setZones] = useState<Zone[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedZone, setSelectedZone] = useState<string>('all');
  const [selectedDevices, setSelectedDevices] = useState<string[]>([]);
  const [activeStreams, setActiveStreams] = useState<CameraStream[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [zonesResponse, devicesResponse] = await Promise.all([
        apiService.getZones(),
        apiService.getDevices({ status: 'active' })
      ]);

      setZones(zonesResponse.results);
      setDevices(devicesResponse.results.filter(device => device.device_type === 'camera'));
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Error al cargar los datos. Verifique la conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  }, []);

  const filteredDevices = selectedZone === 'all' 
    ? devices 
    : devices.filter(device => device.zone_name === zones.find(z => z.id === selectedZone)?.name);

  const statusFilteredDevices = statusFilter === 'all'
    ? filteredDevices
    : filteredDevices.filter(device => device.status === statusFilter);

  const deviceStats = {
    total: filteredDevices.length,
    active: filteredDevices.filter(d => d.status === 'active').length,
    streaming: activeStreams.length,
    selected: selectedDevices.length
  };

  const toggleCameraStream = useCallback((deviceId: string) => {
    setActiveStreams(prev => {
      const existingStream = prev.find(stream => stream.deviceId === deviceId);
      
      if (existingStream) {
        return prev.filter(stream => stream.deviceId !== deviceId);
      } else {
        const device = devices.find(d => d.id === deviceId);
        if (device) {
          return [...prev, {
            deviceId,
            isStreaming: true,
            streamUrl: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/devices/${deviceId}/stream/`
          }];
        }
        return prev;
      }
    });
  }, [devices]);

  const startSelectedStreams = useCallback(() => {
    const newStreams = selectedDevices.map(deviceId => ({
      deviceId,
      isStreaming: true,
      streamUrl: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/devices/${deviceId}/stream/`
    }));
    setActiveStreams(newStreams);
  }, [selectedDevices]);

  const stopAllStreams = useCallback(() => {
    setActiveStreams([]);
    setSelectedDevices([]);
  }, []);

  const selectAllCameras = useCallback((devicesToSelect: Device[]) => {
    const deviceIds = devicesToSelect.map(device => device.id);
    setSelectedDevices(deviceIds);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedDevices([]);
    setActiveStreams([]);
  }, []);

  useEffect(() => {
    loadData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    
    return () => clearInterval(interval);
  }, [loadData]);

  return {
    zones,
    devices,
    loading,
    error,
    activeStreams,
    selectedDevices,
    selectedZone,
    statusFilter,
    setSelectedZone,
    setStatusFilter,
    setSelectedDevices,
    toggleCameraStream,
    startSelectedStreams,
    stopAllStreams,
    selectAllCameras,
    clearSelection,
    loadData,
    filteredDevices: statusFilteredDevices,
    deviceStats
  };
}
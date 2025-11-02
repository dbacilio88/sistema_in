'use client';

import { useState, useEffect } from 'react';
import { VideoCameraIcon, CameraIcon, ExclamationTriangleIcon, PlayIcon, StopIcon } from '@heroicons/react/24/outline';
import { VideoPlayer } from './VideoPlayer';
import { MultiStreamView } from './MultiStreamView';
import { useCameraStreams } from '@/hooks/useCameraStreams';

export function RealtimeMonitor() {
  const [mounted, setMounted] = useState(false);
  const {
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
    filteredDevices,
    deviceStats
  } = useCameraStreams();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <VideoCameraIcon className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Monitoreo en Tiempo Real</h1>
        </div>
        <div className="bg-white p-8 rounded-lg border text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando cámaras...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <VideoCameraIcon className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Monitoreo en Tiempo Real</h1>
        </div>
        <div className="bg-white p-8 rounded-lg border text-center">
          <ExclamationTriangleIcon className="h-16 w-16 mx-auto mb-4 text-red-400" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error de Conexión</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadData}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <VideoCameraIcon className="h-8 w-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-gray-900">Monitoreo en Tiempo Real</h1>
      </div>

      {/* Controls */}
      <div className="bg-white p-6 rounded-lg border">
        {/* Statistics Panel */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm text-blue-600 font-medium">Total Cámaras</p>
            <p className="text-2xl font-bold text-blue-900">{deviceStats.total}</p>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <p className="text-sm text-green-600 font-medium">Activas</p>
            <p className="text-2xl font-bold text-green-900">{deviceStats.active}</p>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg">
            <p className="text-sm text-purple-600 font-medium">Transmitiendo</p>
            <p className="text-2xl font-bold text-purple-900">{deviceStats.streaming}</p>
          </div>
          <div className="bg-orange-50 p-3 rounded-lg">
            <p className="text-sm text-orange-600 font-medium">Seleccionadas</p>
            <p className="text-2xl font-bold text-orange-900">{deviceStats.selected}</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4 mb-6">
          <div>
            <label htmlFor="zone-select" className="block text-sm font-medium text-gray-700 mb-1">
              Seleccionar Zona
            </label>
            <select
              id="zone-select"
              value={selectedZone}
              onChange={(e) => setSelectedZone(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">Todas las zonas</option>
              {zones.map(zone => (
                <option key={zone.id} value={zone.id}>
                  {zone.name} ({zone.device_count} cámaras)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Filtrar por Estado
            </label>
            <select
              id="status-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">Todos los estados</option>
              <option value="active">Activas</option>
              <option value="inactive">Inactivas</option>
              <option value="maintenance">En mantenimiento</option>
              <option value="error">Con error</option>
            </select>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => selectAllCameras(filteredDevices)}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm"
            >
              Seleccionar Todas
            </button>
            <button
              onClick={clearSelection}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm"
            >
              Limpiar Selección
            </button>
            <button
              onClick={startSelectedStreams}
              disabled={selectedDevices.length === 0}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm flex items-center gap-2"
            >
              <PlayIcon className="h-4 w-4" />
              Iniciar Transmisión ({selectedDevices.length})
            </button>
            {activeStreams.length > 0 && (
              <button
                onClick={stopAllStreams}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm flex items-center gap-2"
              >
                <StopIcon className="h-4 w-4" />
                Detener Todas ({activeStreams.length})
              </button>
            )}
            <button
              onClick={loadData}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm"
            >
              🔄 Actualizar
            </button>
          </div>
        </div>

        {/* Camera Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredDevices.map(device => {
            const isSelected = selectedDevices.includes(device.id);
            const isStreaming = activeStreams.some(stream => stream.deviceId === device.id);
            const streamData = activeStreams.find(stream => stream.deviceId === device.id);

            return (
              <div
                key={device.id}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => {
                  const newSelection = selectedDevices.includes(device.id) 
                    ? selectedDevices.filter(id => id !== device.id)
                    : [...selectedDevices, device.id];
                  setSelectedDevices(newSelection);
                }}
              >
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-medium text-gray-900">{device.name}</h3>
                    <p className="text-sm text-gray-500">{device.code}</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleCameraStream(device.id);
                    }}
                    className={`p-2 rounded-full ${
                      isStreaming 
                        ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                        : 'bg-green-100 text-green-600 hover:bg-green-200'
                    }`}
                  >
                    {isStreaming ? (
                      <StopIcon className="h-4 w-4" />
                    ) : (
                      <PlayIcon className="h-4 w-4" />
                    )}
                  </button>
                </div>

                {/* Stream Display */}
                <div className="aspect-video mb-3">
                  {isStreaming && streamData ? (
                    <VideoPlayer
                      streamUrl={streamData.streamUrl}
                      deviceName={device.name}
                      className="aspect-video"
                      onError={() => {
                        console.error(`Error streaming from device ${device.code}`);
                        // La función toggleCameraStream manejará la eliminación
                      }}
                    />
                  ) : (
                    <div className="aspect-video bg-gray-100 rounded-md flex items-center justify-center">
                      <div className="text-center">
                        <CameraIcon className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                        <p className="text-sm text-gray-500">
                          {isSelected ? 'Click para transmitir' : 'Seleccionar cámara'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Device Info */}
                <div className="space-y-1 text-xs text-gray-600">
                  <div className="flex justify-between">
                    <span>Zona:</span>
                    <span className="font-medium">{device.zone_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Estado:</span>
                    <span className={`font-medium ${
                      device.status === 'active' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {device.status_display}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Resolución:</span>
                    <span className="font-medium">{device.resolution}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {filteredDevices.length === 0 && (
          <div className="col-span-full text-center py-8">
            <CameraIcon className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No hay cámaras disponibles
            </h3>
            <p className="text-gray-600">
              {selectedZone === 'all' && statusFilter === 'all'
                ? 'No se encontraron cámaras activas en el sistema.'
                : `No se encontraron cámaras ${statusFilter === 'all' ? '' : `con estado '${statusFilter}' `}en ${selectedZone === 'all' ? 'ninguna zona' : 'la zona seleccionada'}.`
              }
            </p>
          </div>
        )}
      </div>

      {/* Multi-Stream View */}
      {activeStreams.length > 0 && (
        <MultiStreamView
          activeStreams={activeStreams}
          devices={devices}
          onRemoveStream={toggleCameraStream}
        />
      )}

      {/* Active Streams Summary */}
      {activeStreams.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <PlayIcon className="h-5 w-5 text-green-600" />
            <h3 className="font-medium text-green-900">
              Transmisiones Activas ({activeStreams.length})
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {activeStreams.map(stream => {
              const device = devices.find(d => d.id === stream.deviceId);
              return (
                <span
                  key={stream.deviceId}
                  className="inline-flex items-center gap-1 bg-green-100 text-green-800 px-2 py-1 rounded text-sm"
                >
                  {device?.name || device?.code}
                  <button
                    onClick={() => toggleCameraStream(stream.deviceId)}
                    className="ml-1 text-green-600 hover:text-green-800"
                  >
                    <StopIcon className="h-3 w-3" />
                  </button>
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
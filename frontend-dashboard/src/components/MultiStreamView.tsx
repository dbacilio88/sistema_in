'use client';

import { useState } from 'react';
import { XMarkIcon, ArrowsPointingOutIcon, ArrowsPointingInIcon } from '@heroicons/react/24/outline';
import { VideoPlayer } from './VideoPlayer';
import { Device } from '@/services/api';

interface MultiStreamViewProps {
  activeStreams: Array<{
    deviceId: string;
    isStreaming: boolean;
    streamUrl: string;
  }>;
  devices: Device[];
  onRemoveStream: (deviceId: string) => void;
  className?: string;
}

export function MultiStreamView({ activeStreams, devices, onRemoveStream, className = '' }: MultiStreamViewProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedStream, setSelectedStream] = useState<string | null>(null);

  if (activeStreams.length === 0) return null;

  const getGridLayout = (count: number) => {
    if (count === 1) return 'grid-cols-1';
    if (count === 2) return 'grid-cols-1 md:grid-cols-2';
    if (count <= 4) return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-2';
    if (count <= 6) return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
    return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4';
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    if (!isFullscreen) {
      setSelectedStream(null);
    }
  };

  const handleStreamClick = (deviceId: string) => {
    if (isFullscreen) {
      setSelectedStream(selectedStream === deviceId ? null : deviceId);
    }
  };

  return (
    <div className={`${className} ${isFullscreen ? 'fixed inset-0 z-50 bg-black' : 'bg-white border rounded-lg'}`}>
      {/* Header */}
      <div className={`flex items-center justify-between p-4 ${isFullscreen ? 'bg-black text-white' : 'border-b'}`}>
        <h3 className="font-medium">
          Transmisiones Activas ({activeStreams.length})
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleFullscreen}
            className={`p-2 rounded-md ${
              isFullscreen 
                ? 'text-white hover:bg-gray-800' 
                : 'text-gray-500 hover:bg-gray-100'
            }`}
            title={isFullscreen ? 'Salir de pantalla completa' : 'Pantalla completa'}
          >
            {isFullscreen ? (
              <ArrowsPointingInIcon className="h-5 w-5" />
            ) : (
              <ArrowsPointingOutIcon className="h-5 w-5" />
            )}
          </button>
          {isFullscreen && (
            <button
              onClick={() => setIsFullscreen(false)}
              className="p-2 rounded-md text-white hover:bg-gray-800"
              title="Cerrar"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      {/* Streams Grid */}
      <div className={`p-4 ${isFullscreen ? 'h-full' : ''}`}>
        {isFullscreen && selectedStream ? (
          // Vista de stream individual en pantalla completa
          <div className="h-full">
            {(() => {
              const stream = activeStreams.find(s => s.deviceId === selectedStream);
              const device = devices.find(d => d.id === selectedStream);
              if (!stream || !device) return null;
              
              return (
                <div className="h-full flex flex-col">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-white text-lg font-medium">{device.name}</h4>
                    <button
                      onClick={() => setSelectedStream(null)}
                      className="text-white hover:bg-gray-800 p-2 rounded-md"
                    >
                      Volver a la grilla
                    </button>
                  </div>
                  <div className="flex-1">
                    <VideoPlayer
                      streamUrl={stream.streamUrl}
                      deviceName={device.name}
                      className="w-full h-full"
                      onError={() => onRemoveStream(device.id)}
                    />
                  </div>
                </div>
              );
            })()}
          </div>
        ) : (
          // Vista de grilla
          <div className={`grid gap-4 ${getGridLayout(activeStreams.length)} ${isFullscreen ? 'h-full' : ''}`}>
            {activeStreams.map(stream => {
              const device = devices.find(d => d.id === stream.deviceId);
              if (!device) return null;

              return (
                <div
                  key={stream.deviceId}
                  className={`relative group ${isFullscreen ? 'cursor-pointer' : ''}`}
                  onClick={() => handleStreamClick(stream.deviceId)}
                >
                  <div className={`relative ${isFullscreen ? 'h-full' : 'aspect-video'}`}>
                    <VideoPlayer
                      streamUrl={stream.streamUrl}
                      deviceName={device.name}
                      className="w-full h-full"
                      onError={() => onRemoveStream(device.id)}
                    />
                    
                    {/* Overlay con controles */}
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onRemoveStream(device.id);
                        }}
                        className="bg-red-500 hover:bg-red-600 text-white p-1 rounded-full"
                        title="Detener transmisión"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                    
                    {/* Información del dispositivo */}
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-2">
                      <div className="text-white">
                        <p className="font-medium text-sm truncate">{device.name}</p>
                        <p className="text-xs opacity-75">{device.code} • {device.zone_name}</p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Instrucciones para pantalla completa */}
      {isFullscreen && !selectedStream && activeStreams.length > 1 && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-75 text-white px-4 py-2 rounded-md text-sm">
          Click en cualquier transmisión para verla en detalle
        </div>
      )}
    </div>
  );
}
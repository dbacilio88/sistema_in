'use client';

import { useState, useRef, useEffect } from 'react';
import { ExclamationTriangleIcon, ArrowsPointingOutIcon } from '@heroicons/react/24/outline';

interface VideoPlayerProps {
  streamUrl: string;
  deviceName: string;
  onError?: () => void;
  className?: string;
}

export function VideoPlayer({ streamUrl, deviceName, onError, className = '' }: VideoPlayerProps) {
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    setError(false);
    setLoading(true);
  }, [streamUrl]);

  const handleError = () => {
    setError(true);
    setLoading(false);
    onError?.();
  };

  const handleLoad = () => {
    setLoading(false);
    setError(false);
  };

  const openFullscreen = () => {
    if (imgRef.current) {
      if (imgRef.current.requestFullscreen) {
        imgRef.current.requestFullscreen();
      }
    }
  };

  if (error) {
    return (
      <div className={`bg-gray-100 rounded-md flex items-center justify-center ${className}`}>
        <div className="text-center p-4">
          <ExclamationTriangleIcon className="h-8 w-8 mx-auto text-red-400 mb-2" />
          <p className="text-sm text-red-600 font-medium">Error de conexión</p>
          <p className="text-xs text-gray-500 mt-1">No se pudo conectar con la cámara</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative bg-gray-100 rounded-md overflow-hidden ${className}`}>
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}
      
      <img
        ref={imgRef}
        src={streamUrl}
        alt={`Stream de ${deviceName}`}
        className="w-full h-full object-cover"
        onError={handleError}
        onLoad={handleLoad}
        style={{ display: error ? 'none' : 'block' }}
      />
      
      {!loading && !error && (
        <button
          onClick={openFullscreen}
          className="absolute top-2 right-2 bg-black bg-opacity-50 text-white p-1 rounded hover:bg-opacity-75 transition-all"
          title="Ver en pantalla completa"
        >
          <ArrowsPointingOutIcon className="h-4 w-4" />
        </button>
      )}
      
      {!loading && !error && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-2">
          <p className="text-white text-xs font-medium truncate">{deviceName}</p>
        </div>
      )}
    </div>
  );
}
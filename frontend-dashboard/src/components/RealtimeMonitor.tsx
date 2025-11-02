'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { 
  VideoCameraIcon, 
  PlayIcon, 
  StopIcon,
  ExclamationTriangleIcon,
  AdjustmentsHorizontalIcon,
  SignalIcon,
  CameraIcon
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';

// Tipos de infracciones disponibles
const INFRACTION_TYPES = [
  { id: 'speeding', label: 'Exceso de Velocidad', color: 'orange' },
  { id: 'red_light', label: 'Luz Roja', color: 'red' },
  { id: 'lane_invasion', label: 'Invasión de Carril', color: 'yellow' }
];

// Tipos de cámaras disponibles
const CAMERA_SOURCES = [
  { id: 'webcam', label: 'Cámara Web Local', type: 'local' },
  { id: 'mobile', label: 'Dispositivo Móvil', type: 'mobile' },
  { id: 'rtsp', label: 'Cámara RTSP', type: 'rtsp' }
];

interface Detection {
  id: string;
  type: 'vehicle' | 'infraction';
  infractionType?: string;
  confidence: number;
  bbox: { x: number; y: number; width: number; height: number };
  timestamp: Date;
  licensePlate?: string;
  speed?: number;
}

export function RealtimeMonitor() {
  console.log('🔄 RealtimeMonitor component loaded - VERSION 2.0 with isDetectionLoopRunning ref');
  
  const [mounted, setMounted] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState<string>('webcam');
  const [selectedInfractions, setSelectedInfractions] = useState<string[]>(['speeding', 'red_light', 'lane_invasion']);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [streamStatus, setStreamStatus] = useState<'idle' | 'connecting' | 'active' | 'error'>('idle');
  const [fps, setFps] = useState(0);
  const [streamUrl, setStreamUrl] = useState('');
  const [showSettings, setShowSettings] = useState(false);

  // Fix hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const isDetectionLoopRunning = useRef<boolean>(false);

  // Configuración de detección
  const [detectionConfig, setDetectionConfig] = useState({
    speedLimit: 60,
    confidenceThreshold: 0.7,
    enableOCR: true,
    enableSpeedDetection: true
  });

  // Limpiar recursos al desmontar
  useEffect(() => {
    return () => {
      stopDetection();
    };
  }, []);

  // Iniciar el loop de detección cuando isDetecting cambie a true
  useEffect(() => {
    console.log('[useEffect] isDetecting changed to:', isDetecting);
    
    if (isDetecting && videoRef.current && canvasRef.current && wsRef.current) {
      console.log('[useEffect] Conditions met, setting isDetectionLoopRunning to true');
      isDetectionLoopRunning.current = true;
      
      // Usar setTimeout para asegurar que el video esté listo
      const timeoutId = setTimeout(() => {
        console.log('[useEffect] Executing detectFrame from useEffect');
        detectFrame();
      }, 200);
      
      return () => {
        clearTimeout(timeoutId);
        console.log('[useEffect] Cleanup - stopping detection loop');
        isDetectionLoopRunning.current = false;
      };
    } else if (!isDetecting) {
      console.log('[useEffect] isDetecting is false, setting isDetectionLoopRunning to false');
      isDetectionLoopRunning.current = false;
    }
  }, [isDetecting]);

  // Iniciar la cámara seleccionada
  const startCamera = async () => {
    try {
      setStreamStatus('connecting');
      
      // Verificar que el navegador soporte getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error(
          'Tu navegador no soporta acceso a la cámara, o estás accediendo desde una conexión no segura. ' +
          'Por favor, accede a la aplicación usando http://localhost:3002 en lugar de una IP.'
        );
      }
      
      if (selectedCamera === 'webcam') {
        // Acceder a la cámara web local
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'environment'
          }
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
          setStreamStatus('active');
        }
      } else if (selectedCamera === 'mobile') {
        // Para móvil, usar el mismo getUserMedia pero con configuración diferente
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'environment'
          }
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
          setStreamStatus('active');
        }
      } else if (selectedCamera === 'rtsp' && streamUrl) {
        // Para RTSP, necesitaremos un proxy en el backend
        // Por ahora, mostraremos un placeholder
        setStreamStatus('active');
        // TODO: Implementar conexión RTSP a través del backend
      }
    } catch (error: any) {
      console.error('Error al acceder a la cámara:', error);
      setStreamStatus('error');
      
      let errorMessage = 'No se pudo acceder a la cámara.';
      
      if (error.name === 'NotAllowedError') {
        errorMessage = 'Permiso denegado. Por favor, permite el acceso a la cámara en tu navegador.';
      } else if (error.name === 'NotFoundError') {
        errorMessage = 'No se encontró ninguna cámara conectada.';
      } else if (error.name === 'NotSupportedError' || error.message.includes('no soporta')) {
        errorMessage = 
          '⚠️ CONTEXTO NO SEGURO DETECTADO\n\n' +
          'El navegador bloquea el acceso a la cámara porque no estás usando HTTPS o localhost.\n\n' +
          '🔧 SOLUCIONES:\n\n' +
          '1. OPCIÓN RECOMENDADA - Configurar Port Forwarding:\n' +
          '   • Cierra el navegador\n' +
          '   • Abre PowerShell como ADMINISTRADOR (Windows + X)\n' +
          '   • Ejecuta: .\\setup-port-forwarding.ps1\n' +
          '   • Accede a http://localhost:3002\n\n' +
          '2. OPCIÓN TEMPORAL - Usar cámara RTSP:\n' +
          '   • Cambia a "Cámara RTSP"\n' +
          '   • Usa una cámara IP en red local\n\n' +
          '3. OPCIÓN ALTERNATIVA - Subir imágenes/videos:\n' +
          '   • Implementar carga de archivos multimedia';
      } else if (error.name === 'NotReadableError') {
        errorMessage = 'La cámara está siendo usada por otra aplicación.';
      }
      
      alert(errorMessage);
    }
  };

  // Detener la cámara
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    setStreamStatus('idle');
  };

  // Iniciar detección
  const startDetection = async () => {
    console.log('[startDetection] Starting camera and WebSocket');
    await startCamera();
    
    // Conectar al WebSocket del backend para detección en tiempo real
    connectWebSocket();
    
    // Establecer estado - el useEffect iniciará el loop de detección
    setIsDetecting(true);
    console.log('[startDetection] isDetecting set to true, useEffect will handle detectFrame');
  };

  // Detener detección
  const stopDetection = () => {
    console.log('[stopDetection] Stopping detection');
    setIsDetecting(false);
    isDetectionLoopRunning.current = false;
    stopCamera();
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    
    setDetections([]);
  };

  // Conectar al WebSocket del backend
  const connectWebSocket = () => {
    // Detectar el host dinámicamente
    const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    const wsUrl = process.env.NEXT_PUBLIC_WS_INFERENCE_URL || `ws://${hostname}:8001/api/ws/inference`;
    
    console.log('[WebSocket] Current hostname:', hostname);
    console.log('[WebSocket] Env var:', process.env.NEXT_PUBLIC_WS_INFERENCE_URL);
    console.log('[WebSocket] Final WebSocket URL:', wsUrl);
    console.log('[WebSocket] Attempting to connect to:', wsUrl);
    
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log('[WebSocket] ✅ Successfully connected to:', wsUrl);
      console.log('[WebSocket] ReadyState:', wsRef.current?.readyState, '(1 = OPEN)');
    };
    
    wsRef.current.onmessage = (event) => {
      console.log('[WebSocket] 📨 Received message:', event.data.substring(0, 100));
      try {
        const data = JSON.parse(event.data);
        console.log('[WebSocket] Parsed data:', data);
        handleDetectionResult(data);
      } catch (error) {
        console.error('[WebSocket] ❌ Error parsing message:', error);
      }
    };
    
    wsRef.current.onerror = (error) => {
      console.error('[WebSocket] ❌ Connection error:', error);
      console.error('[WebSocket] URL attempted:', wsUrl);
    };
    
    wsRef.current.onclose = (event) => {
      console.log('[WebSocket] ⚠️ Connection closed. Code:', event.code, 'Reason:', event.reason);
    };
  };

  // Procesar frame y enviar al backend
  const detectFrame = () => {
    console.log('[detectFrame] Starting - isDetectionLoopRunning:', isDetectionLoopRunning.current, 'videoRef:', !!videoRef.current, 'canvasRef:', !!canvasRef.current);
    
    // Usar la ref en lugar del estado para evitar problemas de cierre (closure)
    if (!isDetectionLoopRunning.current || !videoRef.current || !canvasRef.current) {
      console.log('[detectFrame] Early return - missing conditions');
      return;
    }
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    if (!ctx || video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.log('[detectFrame] Video not ready, readyState:', video.readyState, 'expected:', video.HAVE_ENOUGH_DATA);
      animationFrameRef.current = requestAnimationFrame(detectFrame);
      return;
    }
    
    // Ajustar el tamaño del canvas al video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Dibujar el frame del video
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Obtener los datos de la imagen
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    // Enviar al backend via WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('[detectFrame] ✅ WebSocket is OPEN - Sending frame, size:', imageData.length);
      wsRef.current.send(JSON.stringify({
        type: 'frame',
        image: imageData.split(',')[1], // Solo enviar la parte base64
        config: {
          infractions: selectedInfractions,
          speed_limit: detectionConfig.speedLimit,
          confidence_threshold: detectionConfig.confidenceThreshold,
          enable_ocr: detectionConfig.enableOCR,
          enable_speed: detectionConfig.enableSpeedDetection
        }
      }));
    } else {
      const states = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'];
      const stateStr = wsRef.current ? states[wsRef.current.readyState] : 'NULL';
      console.log('[detectFrame] ⚠️ WebSocket not ready - state:', stateStr, '(need OPEN)');
    }
    
    // Dibujar las detecciones actuales
    drawDetections(ctx);
    
    // Continuar con el siguiente frame
    animationFrameRef.current = requestAnimationFrame(detectFrame);
  };

  // Manejar resultados de detección del backend
  const handleDetectionResult = (data: any) => {
    if (data.detections) {
      const newDetections: Detection[] = data.detections.map((det: any, idx: number) => ({
        id: `${Date.now()}-${idx}`,
        type: det.type || 'vehicle',
        infractionType: det.infraction_type,
        confidence: det.confidence,
        bbox: det.bbox,
        timestamp: new Date(),
        licensePlate: det.license_plate,
        speed: det.speed
      }));
      
      setDetections(newDetections);
      
      // Actualizar FPS
      if (data.fps) {
        setFps(data.fps);
      }
    }
  };

  // Dibujar las detecciones en el canvas
  const drawDetections = (ctx: CanvasRenderingContext2D) => {
    detections.forEach((detection) => {
      const { bbox, type, infractionType, confidence, licensePlate, speed } = detection;
      
      // Determinar el color según el tipo de detección
      let color = '#10b981'; // Verde para vehículos
      if (type === 'infraction') {
        if (infractionType === 'speeding') color = '#f97316'; // Naranja
        if (infractionType === 'red_light') color = '#ef4444'; // Rojo
        if (infractionType === 'lane_invasion') color = '#eab308'; // Amarillo
      }
      
      // Dibujar el rectángulo
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);
      
      // Dibujar el fondo para el texto
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.7;
      ctx.fillRect(bbox.x, bbox.y - 25, bbox.width, 25);
      ctx.globalAlpha = 1.0;
      
      // Dibujar el texto
      ctx.fillStyle = '#ffffff';
      ctx.font = '14px Arial';
      ctx.fillText(
        `${type === 'infraction' ? infractionType : 'Vehículo'} ${(confidence * 100).toFixed(0)}%`,
        bbox.x + 5,
        bbox.y - 8
      );
      
      // Si hay placa detectada, mostrarla
      if (licensePlate) {
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.7;
        ctx.fillRect(bbox.x, bbox.y + bbox.height, bbox.width, 25);
        ctx.globalAlpha = 1.0;
        
        ctx.fillStyle = '#ffffff';
        ctx.fillText(licensePlate, bbox.x + 5, bbox.y + bbox.height + 17);
      }
      
      // Si hay velocidad detectada, mostrarla
      if (speed) {
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.7;
        ctx.fillRect(bbox.x, bbox.y + bbox.height + (licensePlate ? 25 : 0), 80, 25);
        ctx.globalAlpha = 1.0;
        
        ctx.fillStyle = '#ffffff';
        ctx.fillText(`${speed} km/h`, bbox.x + 5, bbox.y + bbox.height + (licensePlate ? 25 : 0) + 17);
      }
    });
  };

  // Toggle selección de tipo de infracción
  const toggleInfraction = (id: string) => {
    setSelectedInfractions(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id)
        : [...prev, id]
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Monitoreo en Tiempo Real</h2>
          <p className="mt-1 text-sm text-gray-500">
            Detección de infracciones de tránsito en tiempo real usando IA
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <AdjustmentsHorizontalIcon className="h-5 w-5 mr-2" />
            Configuración
          </button>
          {isDetecting ? (
            <button
              onClick={stopDetection}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
            >
              <StopIcon className="h-5 w-5 mr-2" />
              Detener
            </button>
          ) : (
            <button
              onClick={startDetection}
              disabled={selectedCamera === 'rtsp' && !streamUrl}
              className={clsx(
                "inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white",
                selectedCamera === 'rtsp' && !streamUrl
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-green-600 hover:bg-green-700"
              )}
            >
              <PlayIcon className="h-5 w-5 mr-2" />
              Iniciar Detección
            </button>
          )}
        </div>
      </div>

      {/* Panel de Configuración */}
      {showSettings && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <h3 className="text-lg font-medium text-gray-900">Configuración de Detección</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Límite de velocidad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Límite de Velocidad (km/h)
              </label>
              <input
                type="number"
                value={detectionConfig.speedLimit}
                onChange={(e) => setDetectionConfig(prev => ({ ...prev, speedLimit: parseInt(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="20"
                max="120"
              />
            </div>

            {/* Umbral de confianza */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Umbral de Confianza ({(detectionConfig.confidenceThreshold * 100).toFixed(0)}%)
              </label>
              <input
                type="range"
                value={detectionConfig.confidenceThreshold}
                onChange={(e) => setDetectionConfig(prev => ({ ...prev, confidenceThreshold: parseFloat(e.target.value) }))}
                className="w-full"
                min="0.5"
                max="0.95"
                step="0.05"
              />
            </div>

            {/* Opciones adicionales */}
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={detectionConfig.enableOCR}
                  onChange={(e) => setDetectionConfig(prev => ({ ...prev, enableOCR: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Detección de Placas (OCR)</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={detectionConfig.enableSpeedDetection}
                  onChange={(e) => setDetectionConfig(prev => ({ ...prev, enableSpeedDetection: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Detección de Velocidad</span>
              </label>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Panel de Control */}
        <div className="space-y-6">
          {/* Selección de Cámara */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <CameraIcon className="h-5 w-5 mr-2" />
              Fuente de Video
            </h3>
            <div className="space-y-3">
              {CAMERA_SOURCES.map((camera) => (
                <button
                  key={camera.id}
                  onClick={() => setSelectedCamera(camera.id)}
                  disabled={isDetecting}
                  className={clsx(
                    'w-full text-left px-4 py-3 rounded-lg border-2 transition-colors',
                    selectedCamera === camera.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300',
                    isDetecting && 'opacity-50 cursor-not-allowed'
                  )}
                >
                  <div className="font-medium text-gray-900">{camera.label}</div>
                  <div className="text-sm text-gray-500">{camera.type}</div>
                </button>
              ))}
              
              {/* URL RTSP */}
              {selectedCamera === 'rtsp' && (
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL RTSP
                  </label>
                  <input
                    type="text"
                    value={streamUrl}
                    onChange={(e) => setStreamUrl(e.target.value)}
                    placeholder="rtsp://..."
                    disabled={isDetecting}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Tipos de Infracciones */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
              Tipos de Infracciones
            </h3>
            <div className="space-y-3">
              {INFRACTION_TYPES.map((infraction) => (
                <label key={infraction.id} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedInfractions.includes(infraction.id)}
                    onChange={() => toggleInfraction(infraction.id)}
                    disabled={isDetecting}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm text-gray-700">{infraction.label}</span>
                  <span
                    className={clsx(
                      'ml-auto w-3 h-3 rounded-full',
                      infraction.color === 'green' && 'bg-green-500',
                      infraction.color === 'orange' && 'bg-orange-500',
                      infraction.color === 'red' && 'bg-red-500',
                      infraction.color === 'yellow' && 'bg-yellow-500'
                    )}
                  />
                </label>
              ))}
            </div>
          </div>

          {/* Estado */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <SignalIcon className="h-5 w-5 mr-2" />
              Estado
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Stream:</span>
                <span className={clsx(
                  'px-2 py-1 text-xs font-medium rounded-full',
                  streamStatus === 'active' && 'bg-green-100 text-green-800',
                  streamStatus === 'connecting' && 'bg-yellow-100 text-yellow-800',
                  streamStatus === 'idle' && 'bg-gray-100 text-gray-800',
                  streamStatus === 'error' && 'bg-red-100 text-red-800'
                )}>
                  {streamStatus === 'active' && 'Activo'}
                  {streamStatus === 'connecting' && 'Conectando'}
                  {streamStatus === 'idle' && 'Inactivo'}
                  {streamStatus === 'error' && 'Error'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Detección:</span>
                <span className={clsx(
                  'px-2 py-1 text-xs font-medium rounded-full',
                  isDetecting ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                )}>
                  {isDetecting ? 'Activa' : 'Inactiva'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">FPS:</span>
                <span className="text-sm font-medium text-gray-900">{fps.toFixed(1)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Detecciones:</span>
                <span className="text-sm font-medium text-gray-900">{detections.length}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Video y Canvas */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="relative bg-gray-900 aspect-video">
              {streamStatus === 'idle' && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <VideoCameraIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-400">
                      Selecciona una fuente de video y presiona "Iniciar Detección"
                    </p>
                  </div>
                </div>
              )}
              
              {streamStatus === 'connecting' && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                    <p className="text-white">Conectando a la cámara...</p>
                  </div>
                </div>
              )}
              
              {streamStatus === 'error' && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <ExclamationTriangleIcon className="h-16 w-16 text-red-400 mx-auto mb-4" />
                    <p className="text-red-400">
                      Error al conectar con la cámara
                    </p>
                    <p className="text-gray-400 text-sm mt-2">
                      Verifica los permisos y la conexión
                    </p>
                  </div>
                </div>
              )}
              
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="absolute inset-0 w-full h-full object-contain"
                style={{ display: streamStatus === 'active' ? 'block' : 'none' }}
              />
              
              <canvas
                ref={canvasRef}
                className="absolute inset-0 w-full h-full object-contain"
                style={{ display: isDetecting ? 'block' : 'none' }}
              />
            </div>
            
            {/* Leyenda */}
            {isDetecting && (
              <div className="p-4 bg-gray-50 border-t border-gray-200">
                <div className="flex flex-wrap gap-4 text-sm">
                  <div className="flex items-center">
                    <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
                    <span className="text-gray-600">Vehículo Detectado</span>
                  </div>
                  {selectedInfractions.includes('speeding') && (
                    <div className="flex items-center">
                      <div className="w-4 h-4 bg-orange-500 rounded mr-2"></div>
                      <span className="text-gray-600">Exceso de Velocidad</span>
                    </div>
                  )}
                  {selectedInfractions.includes('red_light') && (
                    <div className="flex items-center">
                      <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
                      <span className="text-gray-600">Luz Roja</span>
                    </div>
                  )}
                  {selectedInfractions.includes('lane_invasion') && (
                    <div className="flex items-center">
                      <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
                      <span className="text-gray-600">Invasión de Carril</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Lista de Detecciones Recientes */}
          {detections.length > 0 && (
            <div className="mt-6 bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Detecciones Recientes</h3>
              </div>
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {detections.slice().reverse().slice(0, 10).map((detection) => (
                  <div key={detection.id} className="px-6 py-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center">
                          <span className={clsx(
                            'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                            detection.type === 'infraction' && detection.infractionType === 'speeding' && 'bg-orange-100 text-orange-800',
                            detection.type === 'infraction' && detection.infractionType === 'red_light' && 'bg-red-100 text-red-800',
                            detection.type === 'infraction' && detection.infractionType === 'lane_invasion' && 'bg-yellow-100 text-yellow-800',
                            detection.type === 'vehicle' && 'bg-green-100 text-green-800'
                          )}>
                            {detection.type === 'infraction' 
                              ? INFRACTION_TYPES.find(i => i.id === detection.infractionType)?.label
                              : 'Vehículo'}
                          </span>
                          <span className="ml-2 text-sm text-gray-500">
                            Confianza: {(detection.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                        {detection.licensePlate && (
                          <div className="mt-1 text-sm text-gray-600">
                            Placa: <span className="font-mono font-medium">{detection.licensePlate}</span>
                          </div>
                        )}
                        {detection.speed && (
                          <div className="mt-1 text-sm text-gray-600">
                            Velocidad: <span className="font-medium">{detection.speed} km/h</span>
                          </div>
                        )}
                      </div>
                      <div className="text-sm text-gray-500">
                        {mounted && detection.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { ExclamationTriangleIcon, ArrowsPointingOutIcon, VideoCameraIcon } from '@heroicons/react/24/outline';

interface Detection {
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  confidence: number;
  vehicle_type?: string;
  license_plate?: string | null;
  speed?: number | null;
  infraction_type?: string;
}

interface LocalWebcamDetectionProps {
  onError?: () => void;
  className?: string;
}

export function LocalWebcamDetection({ 
  onError, 
  className = '' 
}: LocalWebcamDetectionProps) {
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [fps, setFps] = useState(0);
  const [detectionCount, setDetectionCount] = useState(0);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [processingFps, setProcessingFps] = useState(0);
  
  // Infraction config
  const [simulateInfractions, setSimulateInfractions] = useState(true);
  const [speedLimit, setSpeedLimit] = useState(60);
  const [enableOCR, setEnableOCR] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(Date.now());
  const lastDetectionsRef = useRef<Detection[]>([]);
  const processingFrameRef = useRef(false);
  const skipFramesRef = useRef(0);
  const processedCountRef = useRef(0);
  const lastProcessTimeRef = useRef(Date.now());
  const isStreamingRef = useRef(false);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Get color scheme for detections
  const getDetectionColor = (detection: Detection) => {
    if (detection.infraction_type) {
      return {
        stroke: '#ff0000',
        fill: 'rgba(255, 0, 0, 0.8)',
        text: '#ffffff'
      };
    }
    
    const vehicleColors: Record<string, { stroke: string; fill: string; text: string }> = {
      'car': { stroke: '#00ff00', fill: 'rgba(0, 255, 0, 0.8)', text: '#000000' },
      'truck': { stroke: '#ff9800', fill: 'rgba(255, 152, 0, 0.8)', text: '#000000' },
      'bus': { stroke: '#2196f3', fill: 'rgba(33, 150, 243, 0.8)', text: '#ffffff' },
      'motorcycle': { stroke: '#9c27b0', fill: 'rgba(156, 39, 176, 0.8)', text: '#ffffff' },
      'bicycle': { stroke: '#ffeb3b', fill: 'rgba(255, 235, 59, 0.8)', text: '#000000' },
      'person': { stroke: '#ff5722', fill: 'rgba(255, 87, 34, 0.8)', text: '#ffffff' }
    };
    
    const vehicleType = detection.vehicle_type?.toLowerCase() || 'car';
    return vehicleColors[vehicleType] || vehicleColors['car'];
  };

  // Draw detections on canvas
  const drawDetections = useCallback((
    ctx: CanvasRenderingContext2D,
    detections: Detection[]
  ) => {
    detections.forEach((detection) => {
      const { bbox, confidence, vehicle_type, license_plate, speed, infraction_type } = detection;
      const colors = getDetectionColor(detection);
      
      // Draw bounding box
      ctx.strokeStyle = colors.stroke;
      ctx.lineWidth = 3;
      ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);
      
      // Prepare label text
      const labels: string[] = [];
      if (vehicle_type) labels.push(vehicle_type);
      if (confidence) labels.push(`${(confidence * 100).toFixed(1)}%`);
      if (license_plate) labels.push(license_plate);
      if (speed !== null && speed !== undefined) labels.push(`${speed.toFixed(1)} km/h`);
      if (infraction_type) labels.push(`⚠️ ${infraction_type}`);
      
      const label = labels.join(' | ');
      
      // Draw label background
      ctx.font = '14px Arial';
      const textMetrics = ctx.measureText(label);
      const textHeight = 20;
      const padding = 4;
      
      const labelX = bbox.x;
      const labelY = bbox.y > textHeight + padding ? bbox.y - textHeight - padding : bbox.y + bbox.height + padding;
      
      ctx.fillStyle = colors.fill;
      ctx.fillRect(
        labelX,
        labelY,
        textMetrics.width + padding * 2,
        textHeight
      );
      
      // Draw label text
      ctx.fillStyle = colors.text;
      ctx.fillText(label, labelX + padding, labelY + 15);
    });
  }, []);

  // Send frame to inference service (non-blocking)
  const sendFrameToInference = useCallback(async () => {
    // Check WebSocket state first
    if (!wsRef.current) {
      console.log('🔍 No WebSocket connection');
      return;
    }
    
    if (wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket not ready. State:', {
        current: wsRef.current.readyState,
        CONNECTING: WebSocket.CONNECTING,
        OPEN: WebSocket.OPEN,
        CLOSING: WebSocket.CLOSING,
        CLOSED: WebSocket.CLOSED
      });
      return;
    }

    if (!videoRef.current || !canvasRef.current) {
      console.log('🔍 Missing video or canvas ref');
      return;
    }

    // Skip if already processing a frame
    if (processingFrameRef.current) {
      return;
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return;

    // Only process every 3rd frame to improve performance
    skipFramesRef.current++;
    if (skipFramesRef.current < 3) {
      return;
    }
    console.log('🎯 Processing frame (every 3rd frame)');
    skipFramesRef.current = 0;

    processingFrameRef.current = true;

    try {
      // Create a temporary canvas for sending
      const tempCanvas = document.createElement('canvas');
      const tempCtx = tempCanvas.getContext('2d');
      
      if (!tempCtx) {
        processingFrameRef.current = false;
        return;
      }

      // Reduce resolution for processing (increases speed)
      const scale = 0.5; // Process at 50% resolution
      tempCanvas.width = video.videoWidth * scale;
      tempCanvas.height = video.videoHeight * scale;
      
      // Draw scaled image
      tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
      
      // Convert to base64 with lower quality for speed
      const imageData = tempCanvas.toDataURL('image/jpeg', 0.6);
      const base64Data = imageData.split(',')[1];
      
      console.log('📤 Sending frame:', {
        size: Math.round(base64Data.length / 1024) + ' KB',
        resolution: `${tempCanvas.width}x${tempCanvas.height}`,
        wsState: wsRef.current.readyState
      });
      
      // Send to inference service (non-blocking)
      const message = JSON.stringify({
        type: 'frame',
        image: base64Data,
        config: {
          confidence_threshold: 0.5,
          enable_ocr: enableOCR,
          simulate_infractions: simulateInfractions,
          infractions: simulateInfractions ? ['speeding'] : [],
          speed_limit: speedLimit,
          process_interval: 1
        }
      });

      wsRef.current.send(message);

      // Update processing FPS
      processedCountRef.current++;
      const now = Date.now();
      const elapsed = now - lastProcessTimeRef.current;
      if (elapsed >= 1000) {
        setProcessingFps(processedCountRef.current);
        processedCountRef.current = 0;
        lastProcessTimeRef.current = now;
      }

    } catch (err) {
      console.error('❌ Error sending frame:', err);
      processingFrameRef.current = false;
    }
  }, [simulateInfractions, speedLimit, enableOCR]); // Add dependencies for config

  // Continuous rendering loop (runs at full FPS) - NOW ONLY FOR FPS COUNTING
  const renderLoop = useCallback(() => {
    // Critical check: ensure we should still be running
    if (!isStreamingRef.current) {
      console.log('⏸️ renderLoop: streaming stopped');
      return;
    }
    
    // NOTE: Frame drawing is now done in ws.onmessage (backend sends processed frames)
    // This loop just counts FPS and sends frames to backend
    
    // Update display FPS
    frameCountRef.current++;
    const now = Date.now();
    const elapsed = now - lastTimeRef.current;
    if (elapsed >= 1000) {
      setFps(frameCountRef.current);
      frameCountRef.current = 0;
      lastTimeRef.current = now;
    }

    // Send frame to inference (non-blocking, throttled)
    sendFrameToInference();
    
    // Continue loop
    if (isStreamingRef.current) {
      animationFrameRef.current = requestAnimationFrame(renderLoop);
    }
  }, [sendFrameToInference]);

  // Start webcam
  const startWebcam = async () => {
    // Prevent multiple connections
    if (isStreamingRef.current || wsRef.current) {
      console.log('⚠️ Already streaming, ignoring start request');
      return;
    }
    
    console.log('🎬 Starting webcam...');
    setLoading(true);
    setError(false);
    setPermissionDenied(false);

    try {
      // Request webcam access
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      });

      streamRef.current = stream;

      // CRITICAL: Wait for video element to be ready BEFORE starting WebSocket
      if (!videoRef.current) {
        console.error('❌ Video ref not available');
        throw new Error('Video element not found');
      }

      const video = videoRef.current;
      video.srcObject = stream;
      
      // Wait for video to be ready
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Video load timeout'));
        }, 5000);

        video.onloadedmetadata = () => {
          clearTimeout(timeout);
          console.log('✅ Video metadata loaded:', video.videoWidth, 'x', video.videoHeight);
          resolve();
        };

        video.onerror = (err) => {
          clearTimeout(timeout);
          reject(err);
        };
      });

      // Play video
      await video.play();
      console.log('▶️ Video playing');

      // CRITICAL: Verify canvas ref is also available
      if (!canvasRef.current) {
        console.error('❌ Canvas ref not available');
        throw new Error('Canvas element not found');
      }

      console.log('✅ Both refs ready - video:', !!videoRef.current, 'canvas:', !!canvasRef.current);

      // NOW connect to inference WebSocket
      const inferenceWsUrl = process.env.NEXT_PUBLIC_INFERENCE_WS || 'ws://localhost:8001';
      const wsUrl = `${inferenceWsUrl}/api/ws/inference`;
      
      console.log('Connecting to WebSocket:', wsUrl);
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected for local webcam');
        
        // Send config with infraction detection enabled
        try {
          const config = {
            type: 'config',
            data: {
              confidence_threshold: 0.5,
              enable_ocr: enableOCR,
              simulate_infractions: simulateInfractions,
              infractions: ['speeding'],
              speed_limit: speedLimit
            }
          };
          ws.send(JSON.stringify(config));
          console.log('📤 Sent config:', config);
        } catch (err) {
          console.error('❌ Error sending initial config:', err);
        }
        
        // Set streaming flag and start render loop
        isStreamingRef.current = true;
        setStreaming(true);
        setLoading(false);
        
        // START RENDER LOOP NOW (after refs are confirmed ready)
        console.log('🎨 Starting render loop...');
        renderLoop();
        
        // Clear any existing ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        
        // Send ping to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            try {
              ws.send(JSON.stringify({ type: 'ping' }));
              console.log('💓 Ping sent');
            } catch (err) {
              console.error('❌ Error sending ping:', err);
              if (pingIntervalRef.current) {
                clearInterval(pingIntervalRef.current);
                pingIntervalRef.current = null;
              }
            }
          } else {
            if (pingIntervalRef.current) {
              clearInterval(pingIntervalRef.current);
              pingIntervalRef.current = null;
            }
          }
        }, 5000); // Ping every 5 seconds
        
        // Render loop already started above - no need to start again
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          console.log('📥 Received from server:', {
            type: data.type,
            hasDetections: !!data.detections,
            detectionCount: data.detections?.length || 0,
            hasFrame: !!data.frame
          });
          
          // Handle pong response
          if (data.type === 'pong') {
            return;
          }
          
          // CRITICAL: Display the processed frame from backend (has boxes drawn)
          if (data.frame && canvasRef.current) {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            
            if (ctx) {
              // Create image from base64
              const img = new Image();
              img.onload = () => {
                // Set canvas size to match image
                canvas.width = img.width;
                canvas.height = img.height;
                // Draw processed frame (with boxes already drawn by backend)
                ctx.drawImage(img, 0, 0);
                console.log('🎨 Drew processed frame on canvas:', img.width, 'x', img.height);
              };
              img.src = `data:image/jpeg;base64,${data.frame}`;
            }
          }
          
          // Store detections for stats
          if (data.detections) {
            setDetectionCount(data.detections.length);
            processingFrameRef.current = false;
          } else {
            processingFrameRef.current = false;
          }
        } catch (err) {
          console.error('❌ Error parsing WebSocket message:', err);
          processingFrameRef.current = false;
        }
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        console.error('Failed to connect to:', wsUrl);
        console.error('Make sure the inference service is running on port 8001');
        setError(true);
        setLoading(false);
        setStreaming(false);
        onError?.();
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket closed:', {
          code: event.code,
          reason: event.reason || 'No reason provided',
          wasClean: event.wasClean
        });
        isStreamingRef.current = false;
        setStreaming(false);
        
        // Common close codes:
        // 1000 = Normal closure
        // 1001 = Going away (page unload)
        // 1005 = No status code (can be normal)
        // 1006 = Abnormal closure (no close frame)
        // 1011 = Server error
        
        if (event.code === 1006) {
          console.error('❌ WebSocket closed abnormally - possible server crash or network issue');
          setError(true);
        } else if (event.code === 1011) {
          console.error('❌ Server error caused WebSocket to close');
          setError(true);
        } else if (event.code !== 1000 && event.code !== 1001 && event.code !== 1005) {
          console.warn('⚠️ WebSocket closed with unusual code:', event.code);
          // Don't set error for code 1005 as it can be normal
        }
      };

    } catch (err: any) {
      console.error('Error accessing webcam:', err);
      
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setPermissionDenied(true);
      } else {
        setError(true);
      }
      
      setLoading(false);
      onError?.();
    }
  };

  // Stop webcam
  const stopWebcam = () => {
    console.log('🛑 Stopping webcam...');
    
    // Stop streaming flag
    isStreamingRef.current = false;
    
    // Stop animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    // Clear ping interval
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Stop video element
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setStreaming(false);
    setDetectionCount(0);
    setFps(0);
  };

  // Cleanup on unmount - properly stop everything
  useEffect(() => {
    console.log('🎬 Component mounted');
    
    return () => {
      console.log('🛑 Component unmounting - stopping all processes');
      // Immediately stop streaming flag to prevent renderLoop from continuing
      isStreamingRef.current = false;
      
      // Cancel animation frame
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      
      // Clear intervals
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
      
      // Close WebSocket
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
        wsRef.current = null;
      }
      
      // Stop media stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, []);
  
  // Cleanup on page unload
  useEffect(() => {
    const handleBeforeUnload = () => {
      console.log('🚪 Page unloading - cleaning up immediately');
      stopWebcam();
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const openFullscreen = () => {
    if (canvasRef.current) {
      if (canvasRef.current.requestFullscreen) {
        canvasRef.current.requestFullscreen();
      }
    }
  };

  if (permissionDenied) {
    return (
      <div className={`bg-gray-100 rounded-md flex items-center justify-center ${className}`}>
        <div className="text-center p-4">
          <VideoCameraIcon className="h-8 w-8 mx-auto text-orange-400 mb-2" />
          <p className="text-sm text-orange-600 font-medium">Permiso de cámara denegado</p>
          <p className="text-xs text-gray-500 mt-1">Por favor permite el acceso a la cámara en tu navegador</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-gray-100 rounded-md flex items-center justify-center ${className}`}>
        <div className="text-center p-6">
          <ExclamationTriangleIcon className="h-12 w-12 mx-auto text-red-400 mb-3" />
          <p className="text-sm text-red-600 font-medium mb-2">Error de conexión</p>
          <p className="text-xs text-gray-600 mb-3">No se pudo conectar con el servicio de detección</p>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 mb-3">
            <p className="text-xs text-yellow-800 font-medium mb-2">📋 Verifica que el servicio esté corriendo:</p>
            <div className="text-left text-xs text-yellow-700 space-y-1 font-mono bg-yellow-100 p-2 rounded">
              <div>cd inference-service</div>
              <div>python -m uvicorn app.main:app --reload --port 8001</div>
            </div>
          </div>
          
          <button
            onClick={() => {
              setError(false);
              startWebcam();
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm"
          >
            🔄 Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative bg-gray-900 rounded-md overflow-hidden ${className}`}>
      {!streaming && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
          <div className="text-center">
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-white text-sm">Iniciando cámara...</p>
              </>
            ) : (
              <>
                <VideoCameraIcon className="h-12 w-12 mx-auto text-gray-400 mb-3" />
                
                {/* Infraction Configuration */}
                <div className="bg-gray-800 rounded-md p-4 mb-4 text-left max-w-md mx-auto">
                  <h3 className="text-white text-sm font-semibold mb-3">⚙️ Configuración de Detección</h3>
                  
                  <div className="space-y-3">
                    {/* Simulate Infractions Toggle */}
                    <div className="flex items-center justify-between">
                      <label className="text-gray-300 text-xs">Simular Infracciones</label>
                      <button
                        onClick={() => setSimulateInfractions(!simulateInfractions)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          simulateInfractions ? 'bg-blue-600' : 'bg-gray-600'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            simulateInfractions ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>

                    {/* Speed Limit */}
                    <div className="flex items-center justify-between">
                      <label className="text-gray-300 text-xs">Límite Velocidad (km/h)</label>
                      <input
                        type="number"
                        value={speedLimit}
                        onChange={(e) => setSpeedLimit(Number(e.target.value))}
                        className="bg-gray-700 text-white text-xs px-2 py-1 rounded w-16 text-center"
                        min="30"
                        max="120"
                      />
                    </div>

                    {/* Enable OCR */}
                    <div className="flex items-center justify-between">
                      <label className="text-gray-300 text-xs">Detectar Placas (OCR)</label>
                      <button
                        onClick={() => setEnableOCR(!enableOCR)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          enableOCR ? 'bg-blue-600' : 'bg-gray-600'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            enableOCR ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>

                    {/* Info */}
                    <div className="bg-blue-900 bg-opacity-30 border border-blue-700 rounded p-2 mt-3">
                      <p className="text-blue-300 text-xs">
                        {simulateInfractions 
                          ? '🎲 Los vehículos detectados tendrán 33% de probabilidad de cometer infracciones de velocidad'
                          : '📊 Solo se detectarán vehículos sin simular infracciones'}
                      </p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={startWebcam}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md text-sm font-semibold"
                >
                  🎥 Iniciar Detección
                </button>
              </>
            )}
          </div>
        </div>
      )}
      
      {/* Hidden video element */}
      <video
        ref={videoRef}
        className="hidden"
        playsInline
        muted
      />
      
      {/* Canvas for drawing detections */}
      <canvas
        ref={canvasRef}
        className="w-full h-full object-contain"
      />
      
      {streaming && (
        <>
          {/* Stats overlay */}
          <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs space-y-1">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              <span>Webcam Local</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span>Render:</span>
              <span className="font-mono font-bold">{fps} FPS</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span>AI:</span>
              <span className="font-mono font-bold">{processingFps} FPS</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span>Detecciones:</span>
              <span className="font-mono font-bold">{detectionCount}</span>
            </div>
            {simulateInfractions && (
              <div className="border-t border-gray-600 pt-1 mt-1">
                <div className="flex items-center gap-1">
                  <span>🚨</span>
                  <span className="text-yellow-400 text-[10px]">Simulación Activa</span>
                </div>
                <div className="text-[10px] text-gray-400">Límite: {speedLimit} km/h</div>
              </div>
            )}
          </div>

          {/* Fullscreen button */}
          <button
            onClick={openFullscreen}
            className="absolute top-2 right-2 bg-black bg-opacity-50 text-white p-1 rounded hover:bg-opacity-75 transition-all"
            title="Ver en pantalla completa"
          >
            <ArrowsPointingOutIcon className="h-4 w-4" />
          </button>

          {/* Stop button */}
          <button
            onClick={stopWebcam}
            className="absolute bottom-2 right-2 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
          >
            Detener
          </button>

          {/* Color legend */}
          <div className="absolute bottom-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 border-2 border-green-500"></div>
                <span>Auto</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 border-2 border-orange-500"></div>
                <span>Camión</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 border-2 border-blue-500"></div>
                <span>Bus</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 border-2 border-purple-500"></div>
                <span>Moto</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 border-2 border-red-500"></div>
                <span>Infracción</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

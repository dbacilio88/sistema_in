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
          confidence_threshold: 0.7,
          enable_ocr: false, // Disable OCR for speed
          enable_speed: false,
          infractions: [],
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
  }, []);

  // Continuous rendering loop (runs at full FPS)
  const renderLoop = useCallback(() => {
    console.log('🔄 renderLoop called, isStreamingRef:', isStreamingRef.current);
    
    if (!videoRef.current || !canvasRef.current || !isStreamingRef.current) {
      console.log('❌ renderLoop stopped:', {
        hasVideo: !!videoRef.current,
        hasCanvas: !!canvasRef.current,
        streaming: isStreamingRef.current
      });
      return;
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return;

    // Check if video is actually playing
    if (video.readyState < 2) {
      // Video not ready yet, try again
      if (streaming) {
        animationFrameRef.current = requestAnimationFrame(renderLoop);
      }
      return;
    }

    // Set canvas size to match video
    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      console.log('📐 Canvas size set to:', canvas.width, 'x', canvas.height);
    }
    
    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Draw last known detections
    if (lastDetectionsRef.current.length > 0) {
      drawDetections(ctx, lastDetectionsRef.current);
    }
    
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
  }, [drawDetections, sendFrameToInference]);

  // Start webcam
  const startWebcam = async () => {
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

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      // Connect to inference WebSocket
      const inferenceWsUrl = process.env.NEXT_PUBLIC_INFERENCE_WS || 'ws://localhost:8001';
      const wsUrl = `${inferenceWsUrl}/api/ws/inference`;
      
      console.log('Connecting to WebSocket:', wsUrl);
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected for local webcam');
        
        // Send initial config message to keep connection alive
        try {
          ws.send(JSON.stringify({
            type: 'config',
            data: {
              confidence_threshold: 0.7,
              enable_ocr: false,
              enable_speed: false
            }
          }));
          console.log('📤 Sent initial config');
        } catch (err) {
          console.error('❌ Error sending initial config:', err);
        }
        
        isStreamingRef.current = true;
        setStreaming(true);
        setLoading(false);
        
        // Send ping to keep connection alive
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            try {
              ws.send(JSON.stringify({ type: 'ping' }));
              console.log('💓 Ping sent');
            } catch (err) {
              console.error('❌ Error sending ping:', err);
              clearInterval(pingInterval);
            }
          } else {
            clearInterval(pingInterval);
          }
        }, 5000); // Ping every 5 seconds
        
        // Start rendering loop after a short delay to ensure connection is stable
        setTimeout(() => {
          renderLoop();
        }, 100);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          console.log('📥 Received from server:', {
            type: data.type,
            hasDetections: !!data.detections,
            detectionCount: data.detections?.length || 0
          });
          
          // Handle pong response
          if (data.type === 'pong') {
            return;
          }
          
          // Store detections for rendering
          if (data.detections) {
            // Scale detections back to full resolution
            const scaledDetections = data.detections.map((det: Detection) => ({
              ...det,
              bbox: {
                x: det.bbox.x * 2, // Scale back from 50%
                y: det.bbox.y * 2,
                width: det.bbox.width * 2,
                height: det.bbox.height * 2
              }
            }));
            
            lastDetectionsRef.current = scaledDetections;
            setDetectionCount(scaledDetections.length);
            processingFrameRef.current = false; // Allow next frame to be processed
          } else {
            // No detections, still mark as processed
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
    // Stop streaming flag
    isStreamingRef.current = false;
    
    // Stop animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
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

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopWebcam();
    };
  }, []);

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
                <button
                  onClick={startWebcam}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm"
                >
                  Iniciar Webcam
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

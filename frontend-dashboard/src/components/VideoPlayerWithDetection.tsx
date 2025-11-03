'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { ExclamationTriangleIcon, ArrowsPointingOutIcon } from '@heroicons/react/24/outline';

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
}

interface DetectionFrame {
  frame: string; // base64 image
  detections: Detection[];
  timestamp: number;
  frame_number: number;
}

interface VideoPlayerWithDetectionProps {
  deviceId: string;
  deviceName: string;
  onError?: () => void;
  className?: string;
}

export function VideoPlayerWithDetection({ 
  deviceId, 
  deviceName, 
  onError, 
  className = '' 
}: VideoPlayerWithDetectionProps) {
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [fps, setFps] = useState(0);
  const [detectionCount, setDetectionCount] = useState(0);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(Date.now());

  // Draw detections on canvas
  const drawDetections = useCallback((
    ctx: CanvasRenderingContext2D,
    detections: Detection[],
    canvasWidth: number,
    canvasHeight: number
  ) => {
    detections.forEach((detection) => {
      const { bbox, confidence, vehicle_type, license_plate, speed } = detection;
      
      // Draw bounding box
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 3;
      ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);
      
      // Prepare label text
      const labels: string[] = [];
      if (vehicle_type) labels.push(vehicle_type);
      if (confidence) labels.push(`${(confidence * 100).toFixed(1)}%`);
      if (license_plate) labels.push(license_plate);
      if (speed !== null && speed !== undefined) labels.push(`${speed.toFixed(1)} km/h`);
      
      const label = labels.join(' | ');
      
      // Draw label background
      ctx.font = '14px Arial';
      const textMetrics = ctx.measureText(label);
      const textHeight = 20;
      const padding = 4;
      
      const labelX = bbox.x;
      const labelY = bbox.y - textHeight - padding;
      
      ctx.fillStyle = 'rgba(0, 255, 0, 0.8)';
      ctx.fillRect(
        labelX,
        labelY,
        textMetrics.width + padding * 2,
        textHeight
      );
      
      // Draw label text
      ctx.fillStyle = '#000000';
      ctx.fillText(label, labelX + padding, labelY + 15);
    });
  }, []);

  // Handle WebSocket frame
  const handleFrame = useCallback((frameData: DetectionFrame) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Create image from base64
    const img = new Image();
    img.onload = () => {
      // Set canvas size to match image
      canvas.width = img.width;
      canvas.height = img.height;
      
      // Draw image
      ctx.drawImage(img, 0, 0);
      
      // Draw detections
      if (frameData.detections && frameData.detections.length > 0) {
        drawDetections(ctx, frameData.detections, canvas.width, canvas.height);
        setDetectionCount(frameData.detections.length);
      } else {
        setDetectionCount(0);
      }
      
      // Update FPS
      frameCountRef.current++;
      const now = Date.now();
      const elapsed = now - lastTimeRef.current;
      if (elapsed >= 1000) {
        setFps(frameCountRef.current);
        frameCountRef.current = 0;
        lastTimeRef.current = now;
      }
      
      setLoading(false);
      setError(false);
    };
    
    img.onerror = () => {
      console.error('Error loading frame image');
      setError(true);
      setLoading(false);
    };
    
    img.src = `data:image/jpeg;base64,${frameData.frame}`;
  }, [drawDetections]);

  // Connect to WebSocket
  useEffect(() => {
    // First, fetch the camera RTSP URL from Django API
    const fetchCameraUrl = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/devices/${deviceId}/`);
        const data = await response.json();
        
        const rtspUrl = data.rtsp_url || data.connection_url;
        
        if (!rtspUrl) {
          console.error(`No RTSP URL found for device ${deviceId}`);
          setError(true);
          setLoading(false);
          onError?.();
          return;
        }
        
        // Connect to inference WebSocket with camera URL
        const wsUrl = `ws://localhost:8001/stream/ws/camera/${deviceId}?camera_url=${encodeURIComponent(rtspUrl)}`;
        
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log(`WebSocket connected for device ${deviceId}`);
          setConnected(true);
          setLoading(false);
          setError(false);
          
          // Optionally send configuration
          ws.send(JSON.stringify({
            type: 'config',
            config: {
              confidence_threshold: 0.7,
              enable_ocr: true,
              enable_speed: true,
              infractions: ['speeding', 'red_light', 'lane_invasion'],
              speed_limit: 60,
              process_interval: 1
            }
          }));
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'frame') {
              handleFrame({
                frame: data.frame,
                detections: data.detections || [],
                timestamp: data.timestamp,
                frame_number: data.frame_number
              });
            } else if (data.type === 'error') {
              console.error('Stream error:', data.error);
              setError(true);
              setLoading(false);
              onError?.();
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };

        ws.onerror = (err) => {
          console.error(`WebSocket error for device ${deviceId}:`, err);
          setError(true);
          setLoading(false);
          setConnected(false);
          onError?.();
        };

        ws.onclose = () => {
          console.log(`WebSocket closed for device ${deviceId}`);
          setConnected(false);
        };

      } catch (err) {
        console.error('Error fetching camera URL:', err);
        setError(true);
        setLoading(false);
        onError?.();
      }
    };

    fetchCameraUrl();

    // Cleanup
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [deviceId, handleFrame, onError]);

  const openFullscreen = () => {
    if (canvasRef.current) {
      if (canvasRef.current.requestFullscreen) {
        canvasRef.current.requestFullscreen();
      }
    }
  };

  if (error) {
    return (
      <div className={`bg-gray-100 rounded-md flex items-center justify-center ${className}`}>
        <div className="text-center p-4">
          <ExclamationTriangleIcon className="h-8 w-8 mx-auto text-red-400 mb-2" />
          <p className="text-sm text-red-600 font-medium">Error de conexión</p>
          <p className="text-xs text-gray-500 mt-1">No se pudo conectar con el servicio de detección</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative bg-gray-900 rounded-md overflow-hidden ${className}`}>
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-white text-sm">Conectando...</p>
          </div>
        </div>
      )}
      
      <canvas
        ref={canvasRef}
        className="w-full h-full object-contain"
        style={{ display: error ? 'none' : 'block' }}
      />
      
      {!loading && !error && (
        <>
          {/* Stats overlay */}
          <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs space-y-1">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <span>{connected ? 'Conectado' : 'Desconectado'}</span>
            </div>
            <div>FPS: {fps}</div>
            <div>Detecciones: {detectionCount}</div>
          </div>

          {/* Fullscreen button */}
          <button
            onClick={openFullscreen}
            className="absolute top-2 right-2 bg-black bg-opacity-50 text-white p-1 rounded hover:bg-opacity-75 transition-all"
            title="Ver en pantalla completa"
          >
            <ArrowsPointingOutIcon className="h-4 w-4" />
          </button>

          {/* Device name */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-2">
            <p className="text-white text-xs font-medium truncate">{deviceName}</p>
          </div>
        </>
      )}
    </div>
  );
}

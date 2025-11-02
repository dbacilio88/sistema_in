'use client';

import { useState, useEffect, useRef } from 'react';

interface UseWebSocketProps {
  url: string;
  enabled?: boolean;
}

interface WebSocketHook {
  socket: any | null;
  isConnected: boolean;
  error: string | null;
  emit: (event: string, data?: any) => void;
  on: (event: string, handler: (data: any) => void) => void;
  off: (event: string, handler?: (data: any) => void) => void;
}

export function useWebSocket({ url, enabled = true }: UseWebSocketProps): WebSocketHook {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<any | null>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    // Importación dinámica de socket.io-client para evitar problemas de SSR
    const connectSocket = async () => {
      try {
        // Usar default import para socket.io-client
        const socketIO = await import('socket.io-client');
        const io = socketIO.default || socketIO;
        
        const socket = io(url, {
          autoConnect: true,
          reconnection: true,
          reconnectionAttempts: 5,
          reconnectionDelay: 1000,
          timeout: 5000,
        });

        socketRef.current = socket;

        // Event listeners para el estado de conexión
        socket.on('connect', () => {
          console.log('WebSocket conectado');
          setIsConnected(true);
          setError(null);
        });

        socket.on('disconnect', (reason: any) => {
          console.log('WebSocket desconectado:', reason);
          setIsConnected(false);
        });

        socket.on('connect_error', (err: any) => {
          console.error('Error de conexión WebSocket:', err);
          setError(err.message || 'Error de conexión');
          setIsConnected(false);
        });

        socket.on('reconnect', (attemptNumber: any) => {
          console.log('WebSocket reconectado después de', attemptNumber, 'intentos');
          setIsConnected(true);
          setError(null);
        });

        socket.on('reconnect_error', (err: any) => {
          console.error('Error al reconectar WebSocket:', err);
          setError('Error de reconexión');
        });
      } catch (err: any) {
        console.error('Error al cargar socket.io-client:', err);
        setError(err.message || 'Error al inicializar WebSocket');
      }
    };

    connectSocket();

    // Cleanup function
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, [url, enabled]);

  const emit = (event: string, data?: any) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit(event, data);
    } else {
      console.warn('WebSocket no está conectado. No se puede enviar evento:', event);
    }
  };

  const on = (event: string, handler: (data: any) => void) => {
    if (socketRef.current) {
      socketRef.current.on(event, handler);
    }
  };

  const off = (event: string, handler?: (data: any) => void) => {
    if (socketRef.current) {
      if (handler) {
        socketRef.current.off(event, handler);
      } else {
        socketRef.current.off(event);
      }
    }
  };

  return {
    socket: socketRef.current,
    isConnected,
    error,
    emit,
    on,
    off,
  };
}
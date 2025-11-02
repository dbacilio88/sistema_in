/**
 * Servicios API para comunicación con el backend
 * ==============================================
 * 
 * Servicios para interactuar con la API de configuración.
 */

import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// Configurar base URL de la API
const API_BASE_URL = '/api'

// Crear instancia de axios con configuración base
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar token de autenticación
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar respuestas y errores
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Interfaces para tipos de datos
export interface SystemConfig {
  system_name: string
  version: string
  environment: string
  database_url: string
  database_pool_size: number
  database_max_overflow: number
  redis_url: string
  cache_ttl_default: number
  cache_max_memory: string
  storage_backend: string
  storage_endpoint: string
  storage_bucket: string
  log_level: string
  log_format: string
  log_file: string
  log_max_size: string
  log_backup_count: number
  metrics_enabled: boolean
  metrics_port: number
  health_check_interval: number
  jwt_secret_key: string
  jwt_algorithm: string
  jwt_expiration_hours: number
  password_min_length: number
  alert_email_enabled: boolean
  alert_email_smtp: string
  alert_email_from: string
  alert_webhook_url: string
}

export interface CameraConfig {
  camera_id: string
  name: string
  rtsp_url: string
  location: { lat: number; lon: number }
  active: boolean
  fps: number
  resolution: [number, number]
  codec: string
  detection_zones: Array<{
    name: string
    polygon: Array<[number, number]>
  }> | null
  speed_limit: number
  calibration_matrix: number[][] | null
  distortion_coeffs: number[] | null
  recording_enabled: boolean
  snapshot_interval: number
  retention_days: number
}

export interface MLModelConfig {
  model_name: string
  model_path: string
  model_version: string
  confidence_threshold: number
  nms_threshold: number
  input_size: [number, number]
  device: string
  batch_size: number
  half_precision: boolean
  classes: number[] | null
  agnostic_nms: boolean
  max_det: number
  tensorrt: boolean
  onnx: boolean
  openvino: boolean
}

export interface DetectionConfig {
  speed_threshold_warning: number
  speed_threshold_violation: number
  max_disappeared: number
  max_distance: number
  ocr_confidence_threshold: number
  plate_formats: string[] | null
  min_vehicle_area: number
  max_vehicle_area: number
  min_track_length: number
  trajectory_smoothing: boolean
  speed_smoothing_window: number
}

export interface ValidationResult {
  valid: boolean
  errors: Record<string, string[]>
  warnings: string[]
}

export interface ExportResult {
  format: string
  content: string
  timestamp: string
}

export interface SystemStats {
  cameras: {
    total: number
    active: number
    inactive: number
  }
  ml_models: {
    total: number
    models: string[]
  }
  system: {
    environment: string
    version: string
    name: string
  }
}

export interface CameraLocation {
  camera_id: string
  name: string
  location: { lat: number; lon: number }
  active: boolean
  speed_limit: number
}

// Servicios de API
export const configAPI = {
  // Configuración del Sistema
  getSystemConfig: (): Promise<SystemConfig> => {
    return apiClient.get('/config/system')
  },

  updateSystemConfig: (config: Partial<SystemConfig>): Promise<any> => {
    return apiClient.put('/config/system', config)
  },

  // Configuración de Cámaras
  getCameraConfigs: (activeOnly?: boolean): Promise<Record<string, CameraConfig>> => {
    const params = activeOnly ? { active_only: true } : {}
    return apiClient.get('/config/cameras', { params })
  },

  getCameraConfig: (cameraId: string): Promise<CameraConfig> => {
    return apiClient.get(`/config/cameras/${cameraId}`)
  },

  createCameraConfig: (cameraId: string, config: Omit<CameraConfig, 'camera_id'>): Promise<any> => {
    return apiClient.post(`/config/cameras/${cameraId}`, config)
  },

  updateCameraConfig: (cameraId: string, config: Partial<CameraConfig>): Promise<any> => {
    return apiClient.put(`/config/cameras/${cameraId}`, config)
  },

  deleteCameraConfig: (cameraId: string): Promise<any> => {
    return apiClient.delete(`/config/cameras/${cameraId}`)
  },

  updateCameraStatus: (cameraId: string, active: boolean): Promise<any> => {
    return apiClient.patch(`/config/cameras/${cameraId}/status`, null, {
      params: { active }
    })
  },

  // Configuración de Modelos ML
  getMLConfigs: (): Promise<Record<string, MLModelConfig>> => {
    return apiClient.get('/config/ml')
  },

  getMLConfig: (modelName: string): Promise<MLModelConfig> => {
    return apiClient.get(`/config/ml/${modelName}`)
  },

  createMLConfig: (modelName: string, config: Omit<MLModelConfig, 'model_name'>): Promise<any> => {
    return apiClient.post(`/config/ml/${modelName}`, config)
  },

  updateMLConfig: (modelName: string, config: Partial<MLModelConfig>): Promise<any> => {
    return apiClient.put(`/config/ml/${modelName}`, config)
  },

  deleteMLConfig: (modelName: string): Promise<any> => {
    return apiClient.delete(`/config/ml/${modelName}`)
  },

  // Configuración de Detección
  getDetectionConfig: (): Promise<DetectionConfig> => {
    return apiClient.get('/config/detection')
  },

  updateDetectionConfig: (config: Partial<DetectionConfig>): Promise<any> => {
    return apiClient.put('/config/detection', config)
  },

  updateDetectionThreshold: (thresholdType: string, value: number): Promise<any> => {
    return apiClient.patch(`/config/detection/threshold/${thresholdType}`, null, {
      params: { value }
    })
  },

  // Validación
  validateConfigurations: (): Promise<ValidationResult> => {
    return apiClient.post('/config/validate')
  },

  // Importación/Exportación
  exportConfigurations: (format: 'yaml' | 'json'): Promise<ExportResult> => {
    return apiClient.get('/config/export', {
      params: { format }
    })
  },

  importConfigurations: (content: string, format: 'yaml' | 'json'): Promise<any> => {
    return apiClient.post('/config/import', {
      content,
      format
    })
  },

  // Backup
  backupConfigurations: (): Promise<any> => {
    return apiClient.get('/config/backup')
  },

  // Información del Sistema
  getSystemStats: (): Promise<SystemStats> => {
    return apiClient.get('/info/stats')
  },

  getCameraLocations: (): Promise<CameraLocation[]> => {
    return apiClient.get('/info/cameras/locations')
  },

  // Health Check
  healthCheck: (): Promise<any> => {
    return apiClient.get('/health')
  }
}

// Servicios de autenticación (mock por ahora)
export const authAPI = {
  login: async (username: string, password: string): Promise<{ token: string; user: any }> => {
    // Simulación de llamada de autenticación
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (username === 'admin' && password === 'admin') {
      return {
        token: 'mock-jwt-token-12345',
        user: {
          id: '1',
          username: 'admin',
          role: 'administrator'
        }
      }
    }
    
    throw new Error('Credenciales inválidas')
  },

  logout: async (): Promise<void> => {
    // Simulación de logout
    await new Promise(resolve => setTimeout(resolve, 500))
  },

  refreshToken: async (token: string): Promise<{ token: string }> => {
    // Simulación de refresh token
    await new Promise(resolve => setTimeout(resolve, 500))
    return { token: 'new-mock-jwt-token-67890' }
  }
}

// Utilidades para manejo de errores
export const handleAPIError = (error: any): string => {
  if (error.response) {
    // Error de respuesta del servidor
    const status = error.response.status
    const data = error.response.data
    
    if (status === 400) {
      return data.detail || 'Solicitud inválida'
    } else if (status === 401) {
      return 'No autorizado'
    } else if (status === 403) {
      return 'Acceso denegado'
    } else if (status === 404) {
      return 'Recurso no encontrado'
    } else if (status === 500) {
      return 'Error interno del servidor'
    } else {
      return data.detail || `Error del servidor (${status})`
    }
  } else if (error.request) {
    // Error de red
    return 'Error de conexión con el servidor'
  } else {
    // Otro tipo de error
    return error.message || 'Error desconocido'
  }
}

// WebSocket para notificaciones en tiempo real
export class ConfigWebSocket {
  private ws: WebSocket | null = null
  private callbacks: Map<string, Function[]> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  connect() {
    try {
      const wsUrl = `ws://${window.location.host}/ws/config-updates`
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.emit(data.type, data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.attemptReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Error connecting WebSocket:', error)
      this.attemptReconnect()
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  on(event: string, callback: Function) {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, [])
    }
    this.callbacks.get(event)!.push(callback)
  }

  off(event: string, callback: Function) {
    const callbacks = this.callbacks.get(event)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  private emit(event: string, data: any) {
    const callbacks = this.callbacks.get(event)
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Error in WebSocket callback:', error)
        }
      })
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect()
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1))
    } else {
      console.error('Max WebSocket reconnection attempts reached')
    }
  }
}

// Instancia global de WebSocket
export const configWebSocket = new ConfigWebSocket()

export default configAPI
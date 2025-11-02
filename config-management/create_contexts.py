"""
Contextos React para gestión de estado
=====================================

Contextos para manejar el estado global de la aplicación de configuración.
"""

# AuthContext.tsx
auth_context = """import React, { createContext, useContext, useState, useEffect } from 'react'

interface User {
  id: string
  username: string
  role: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  isAuthenticated: boolean
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Verificar token guardado al cargar la aplicación
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')
    
    if (savedToken && savedUser) {
      setToken(savedToken)
      setUser(JSON.parse(savedUser))
    }
    
    setIsLoading(false)
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      // TODO: Implementar llamada real al API de autenticación
      // Por ahora, simulamos login exitoso
      if (username === 'admin' && password === 'admin') {
        const mockUser: User = {
          id: '1',
          username: 'admin',
          role: 'administrator'
        }
        const mockToken = 'mock-jwt-token'
        
        setUser(mockUser)
        setToken(mockToken)
        
        localStorage.setItem('auth_token', mockToken)
        localStorage.setItem('auth_user', JSON.stringify(mockUser))
        
        return true
      }
      
      return false
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isAuthenticated: !!user && !!token,
    isLoading
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}"""

# ConfigContext.tsx
config_context = """import React, { createContext, useContext, useState, useEffect } from 'react'
import { configAPI } from '../services/api'
import toast from 'react-hot-toast'

interface SystemConfig {
  system_name: string
  version: string
  environment: string
  database_url: string
  redis_url: string
  log_level: string
  metrics_enabled: boolean
}

interface CameraConfig {
  camera_id: string
  name: string
  rtsp_url: string
  location: { lat: number; lon: number }
  active: boolean
  speed_limit: number
  fps: number
  resolution: [number, number]
}

interface MLModelConfig {
  model_name: string
  model_path: string
  model_version: string
  confidence_threshold: number
  nms_threshold: number
  device: string
}

interface DetectionConfig {
  speed_threshold_warning: number
  speed_threshold_violation: number
  ocr_confidence_threshold: number
  max_disappeared: number
  max_distance: number
}

interface ConfigContextType {
  // Configuraciones
  systemConfig: SystemConfig | null
  cameraConfigs: Record<string, CameraConfig>
  mlConfigs: Record<string, MLModelConfig>
  detectionConfig: DetectionConfig | null
  
  // Estados de carga
  isLoading: boolean
  isUpdating: boolean
  
  // Métodos
  loadConfigurations: () => Promise<void>
  updateSystemConfig: (config: Partial<SystemConfig>) => Promise<void>
  updateCameraConfig: (cameraId: string, config: Partial<CameraConfig>) => Promise<void>
  updateMLConfig: (modelName: string, config: Partial<MLModelConfig>) => Promise<void>
  updateDetectionConfig: (config: Partial<DetectionConfig>) => Promise<void>
  validateConfigurations: () => Promise<any>
  exportConfigurations: (format: 'yaml' | 'json') => Promise<string>
  importConfigurations: (content: string, format: 'yaml' | 'json') => Promise<void>
  
  // Estadísticas
  stats: {
    totalCameras: number
    activeCameras: number
    totalModels: number
    lastUpdated: Date | null
  }
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined)

export const useConfig = () => {
  const context = useContext(ConfigContext)
  if (context === undefined) {
    throw new Error('useConfig must be used within a ConfigProvider')
  }
  return context
}

export const ConfigProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [systemConfig, setSystemConfig] = useState<SystemConfig | null>(null)
  const [cameraConfigs, setCameraConfigs] = useState<Record<string, CameraConfig>>({})
  const [mlConfigs, setMLConfigs] = useState<Record<string, MLModelConfig>>({})
  const [detectionConfig, setDetectionConfig] = useState<DetectionConfig | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const loadConfigurations = async () => {
    setIsLoading(true)
    try {
      const [system, cameras, models, detection] = await Promise.all([
        configAPI.getSystemConfig(),
        configAPI.getCameraConfigs(),
        configAPI.getMLConfigs(),
        configAPI.getDetectionConfig()
      ])
      
      setSystemConfig(system)
      setCameraConfigs(cameras)
      setMLConfigs(models)
      setDetectionConfig(detection)
      setLastUpdated(new Date())
      
    } catch (error) {
      console.error('Error loading configurations:', error)
      toast.error('Error al cargar configuraciones')
    } finally {
      setIsLoading(false)
    }
  }

  const updateSystemConfig = async (config: Partial<SystemConfig>) => {
    setIsUpdating(true)
    try {
      await configAPI.updateSystemConfig(config)
      setSystemConfig(prev => prev ? { ...prev, ...config } : null)
      setLastUpdated(new Date())
      toast.success('Configuración del sistema actualizada')
    } catch (error) {
      console.error('Error updating system config:', error)
      toast.error('Error al actualizar configuración del sistema')
      throw error
    } finally {
      setIsUpdating(false)
    }
  }

  const updateCameraConfig = async (cameraId: string, config: Partial<CameraConfig>) => {
    setIsUpdating(true)
    try {
      await configAPI.updateCameraConfig(cameraId, config)
      setCameraConfigs(prev => ({
        ...prev,
        [cameraId]: { ...prev[cameraId], ...config }
      }))
      setLastUpdated(new Date())
      toast.success(`Configuración de cámara ${cameraId} actualizada`)
    } catch (error) {
      console.error('Error updating camera config:', error)
      toast.error('Error al actualizar configuración de cámara')
      throw error
    } finally {
      setIsUpdating(false)
    }
  }

  const updateMLConfig = async (modelName: string, config: Partial<MLModelConfig>) => {
    setIsUpdating(true)
    try {
      await configAPI.updateMLConfig(modelName, config)
      setMLConfigs(prev => ({
        ...prev,
        [modelName]: { ...prev[modelName], ...config }
      }))
      setLastUpdated(new Date())
      toast.success(`Configuración de modelo ${modelName} actualizada`)
    } catch (error) {
      console.error('Error updating ML config:', error)
      toast.error('Error al actualizar configuración de modelo')
      throw error
    } finally {
      setIsUpdating(false)
    }
  }

  const updateDetectionConfig = async (config: Partial<DetectionConfig>) => {
    setIsUpdating(true)
    try {
      await configAPI.updateDetectionConfig(config)
      setDetectionConfig(prev => prev ? { ...prev, ...config } : null)
      setLastUpdated(new Date())
      toast.success('Configuración de detección actualizada')
    } catch (error) {
      console.error('Error updating detection config:', error)
      toast.error('Error al actualizar configuración de detección')
      throw error
    } finally {
      setIsUpdating(false)
    }
  }

  const validateConfigurations = async () => {
    try {
      const result = await configAPI.validateConfigurations()
      return result
    } catch (error) {
      console.error('Error validating configurations:', error)
      toast.error('Error al validar configuraciones')
      throw error
    }
  }

  const exportConfigurations = async (format: 'yaml' | 'json') => {
    try {
      const result = await configAPI.exportConfigurations(format)
      return result.content
    } catch (error) {
      console.error('Error exporting configurations:', error)
      toast.error('Error al exportar configuraciones')
      throw error
    }
  }

  const importConfigurations = async (content: string, format: 'yaml' | 'json') => {
    try {
      await configAPI.importConfigurations(content, format)
      await loadConfigurations() // Recargar configuraciones después de importar
      toast.success('Configuraciones importadas exitosamente')
    } catch (error) {
      console.error('Error importing configurations:', error)
      toast.error('Error al importar configuraciones')
      throw error
    }
  }

  // Cargar configuraciones al montar el componente
  useEffect(() => {
    loadConfigurations()
  }, [])

  // Calcular estadísticas
  const stats = {
    totalCameras: Object.keys(cameraConfigs).length,
    activeCameras: Object.values(cameraConfigs).filter(camera => camera.active).length,
    totalModels: Object.keys(mlConfigs).length,
    lastUpdated
  }

  const value: ConfigContextType = {
    systemConfig,
    cameraConfigs,
    mlConfigs,
    detectionConfig,
    isLoading,
    isUpdating,
    loadConfigurations,
    updateSystemConfig,
    updateCameraConfig,
    updateMLConfig,
    updateDetectionConfig,
    validateConfigurations,
    exportConfigurations,
    importConfigurations,
    stats
  }

  return <ConfigContext.Provider value={value}>{children}</ConfigContext.Provider>
}"""

# Crear archivos de contexto
with open("web/src/contexts/AuthContext.tsx", "w") as f:
    f.write(auth_context)

with open("web/src/contexts/ConfigContext.tsx", "w") as f:
    f.write(config_context)

print("✅ Contextos React creados exitosamente")
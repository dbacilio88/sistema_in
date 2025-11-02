import React, { createContext, useContext, useState, useEffect } from 'react'

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

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }: AuthProviderProps) => {
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
}
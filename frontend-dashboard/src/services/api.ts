// API Service for backend communication
// Detectar automáticamente la URL base según el entorno
const getApiBaseUrl = () => {
  // Si estamos en el navegador
  if (typeof window !== 'undefined') {
    // Si hay una variable de entorno configurada, usarla
    if (process.env.NEXT_PUBLIC_API_URL) {
      return process.env.NEXT_PUBLIC_API_URL;
    }
    
    // Si estamos en localhost, usar localhost
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    
    // Si estamos en una IP pública (AWS), usar la misma IP del navegador
    return `http://${window.location.hostname}:8000`;
  }
  
  // Para Server-Side Rendering, usar la variable de entorno o fallback
  return process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export interface Infraction {
  id: string;
  infraction_code: string;
  infraction_type: string;
  infraction_type_display: string;
  severity: string;
  severity_display: string;
  status: string;
  status_display: string;
  device_name: string;
  zone_name: string;
  license_plate_detected: string;
  detected_speed?: number;
  speed_limit?: number;
  fine_amount: string;
  detected_at: string;
  created_at: string;
}

export interface InfractionStats {
  total_infractions: number;
  today: number;
  this_week: number;
  this_month: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  pending_review: number;
}

export interface Device {
  id: string;
  code: string;
  name: string;
  device_type: string;
  status: string;
  status_display: string;
  zone_name: string;
  location_lat: string;
  location_lon: string;
  ip_address: string;
  resolution: string;
  fps: number;
  is_active: boolean;
}

export interface Zone {
  id: string;
  code: string;
  name: string;
  speed_limit: number;
  is_active: boolean;
  device_count: number;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  role_display: string;
  dni?: string;
  phone?: string;
  is_active: boolean;
  date_joined: string;
  last_login?: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
  link?: string;
}

class ApiService {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
    
    // Debug logging
    if (typeof window !== 'undefined') {
      console.log('🔧 API Service initialized');
      console.log('🌐 Base URL:', this.baseURL);
      console.log('🖥️ Window hostname:', window.location.hostname);
      console.log('🔧 NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
      
      this.token = localStorage.getItem('access_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  private async fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (options?.headers) {
      Object.assign(headers, options.headers);
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Infractions
  async getInfractions(params?: { limit?: number; offset?: number; status?: string }): Promise<{ count: number; results: Infraction[] }> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    if (params?.status) queryParams.append('status', params.status);

    return this.fetchAPI<{ count: number; results: Infraction[] }>(
      `/api/infractions/?${queryParams.toString()}`
    );
  }

  async getInfractionStats(): Promise<InfractionStats> {
    return this.fetchAPI<InfractionStats>('/api/infractions/statistics/');
  }

  async getRecentInfractions(): Promise<Infraction[]> {
    return this.fetchAPI<Infraction[]>('/api/infractions/recent/');
  }

  // Devices
  async getDevices(params?: { limit?: number; status?: string }): Promise<{ count: number; results: Device[] }> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);

    return this.fetchAPI<{ count: number; results: Device[] }>(
      `/api/devices/?${queryParams.toString()}`
    );
  }

  async getDeviceStats(): Promise<{ total_devices: number; active: number; by_status: Record<string, number> }> {
    return this.fetchAPI('/api/devices/statistics/');
  }

  // Zones
  async getZones(): Promise<{ count: number; results: Zone[] }> {
    return this.fetchAPI<{ count: number; results: Zone[] }>('/api/devices/zones/');
  }

  // Authentication
  async login(username: string, password: string): Promise<{ access: string; refresh: string; user?: any }> {
    const response = await this.fetchAPI<{ success: boolean; data: { access: string; refresh: string; user: any } }>('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    
    // Handle wrapped response format from Django
    const { access, refresh, user } = response.data || response;
    
    if (access) {
      this.setToken(access);
      if (refresh) {
        localStorage.setItem('refresh_token', refresh);
      }
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
      }
    }
    
    return { access, refresh, user };
  }

  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await this.fetchAPI('/api/auth/logout/', {
          method: 'POST',
          body: JSON.stringify({ refresh: refreshToken }),
        });
      }
    } finally {
      this.clearToken();
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('isAuthenticated');
    }
  }

  // User Profile
  async getCurrentUser(): Promise<{ success: boolean; data: UserProfile }> {
    return this.fetchAPI<{ success: boolean; data: UserProfile }>('/api/auth/users/me/');
  }

  // Notifications
  async getNotifications(params?: { unread_only?: boolean }): Promise<{ count: number; results: Notification[] }> {
    const queryParams = new URLSearchParams();
    if (params?.unread_only) queryParams.append('unread_only', 'true');

    return this.fetchAPI<{ count: number; results: Notification[] }>(
      `/api/notifications/?${queryParams.toString()}`
    );
  }

  async markNotificationAsRead(notificationId: string): Promise<void> {
    await this.fetchAPI(`/api/notifications/${notificationId}/mark_read/`, {
      method: 'POST',
    });
  }

  async markAllNotificationsAsRead(): Promise<void> {
    await this.fetchAPI('/api/notifications/mark_all_read/', {
      method: 'POST',
    });
  }
}

export const apiService = new ApiService();

import { BellIcon, WifiIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { clsx } from 'clsx';
import { useEffect, useState } from 'react';
import { apiService, UserProfile, Notification } from '@/services/api';

interface DashboardHeaderProps {
  isConnected: boolean;
}

export function DashboardHeader({ isConnected }: DashboardHeaderProps) {
  const [mounted, setMounted] = useState(false);
  const [currentTime, setCurrentTime] = useState('');
  const [user, setUser] = useState<UserProfile | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);

  // Fix hydration mismatch
  useEffect(() => {
    setMounted(true);
    setCurrentTime(format(new Date(), 'PPPp', { locale: es }));
  }, []);

  useEffect(() => {
    loadUserData();
    loadNotifications();
    
    // Actualizar notificaciones cada 30 segundos
    const interval = setInterval(() => {
      loadNotifications();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadUserData = async () => {
    try {
      // Primero intentar desde localStorage
      const userStr = localStorage.getItem('user');
      if (userStr) {
        setUser(JSON.parse(userStr));
      }
      
      // Luego actualizar desde la API
      const response = await apiService.getCurrentUser();
      if (response.success && response.data) {
        setUser(response.data);
        localStorage.setItem('user', JSON.stringify(response.data));
      }
    } catch (error) {
      console.error('Error al cargar datos del usuario:', error);
    }
  };

  const loadNotifications = async () => {
    try {
      const response = await apiService.getNotifications({ unread_only: true });
      if (response.results) {
        setNotifications(response.results.slice(0, 5)); // Mostrar solo las 5 más recientes
        setUnreadCount(response.count);
      }
    } catch (error) {
      console.error('Error al cargar notificaciones:', error);
    }
  };

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await apiService.markNotificationAsRead(notificationId);
      loadNotifications();
    } catch (error) {
      console.error('Error al marcar notificación como leída:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await apiService.markAllNotificationsAsRead();
      loadNotifications();
    } catch (error) {
      console.error('Error al marcar todas las notificaciones como leídas:', error);
    }
  };

  const getUserInitials = () => {
    if (!user) return 'U';
    const firstInitial = user.first_name?.charAt(0) || user.username.charAt(0);
    const lastInitial = user.last_name?.charAt(0) || '';
    return (firstInitial + lastInitial).toUpperCase();
  };

  const getUserDisplayName = () => {
    if (!user) return 'Usuario';
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user.username;
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard de Monitoreo</h1>
          {mounted && <p className="text-sm text-gray-500">{currentTime}</p>}
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Indicador de Conexión */}
          <div className="flex items-center space-x-2">
            <WifiIcon 
              className={clsx(
                'w-5 h-5',
                isConnected ? 'text-green-500' : 'text-red-500'
              )} 
            />
            <span className={clsx(
              'text-sm font-medium',
              isConnected ? 'text-green-600' : 'text-red-600'
            )}>
              {isConnected ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
          
          {/* Notificaciones */}
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-gray-400 hover:text-gray-600"
            >
              <BellIcon className="w-6 h-6" />
              {unreadCount > 0 && (
                <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Dropdown de Notificaciones */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900">Notificaciones</h3>
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllAsRead}
                      className="text-xs text-blue-600 hover:text-blue-800"
                    >
                      Marcar todas como leídas
                    </button>
                  )}
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="p-4 text-center text-gray-500">
                      No hay notificaciones nuevas
                    </div>
                  ) : (
                    notifications.map((notification) => (
                      <div
                        key={notification.id}
                        className="p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                        onClick={() => handleMarkAsRead(notification.id)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-sm text-gray-900">
                              {notification.title}
                            </p>
                            <p className="text-xs text-gray-600 mt-1">
                              {notification.message}
                            </p>
                            <p className="text-xs text-gray-400 mt-1">
                              {format(new Date(notification.created_at), 'PPp', { locale: es })}
                            </p>
                          </div>
                          {!notification.is_read && (
                            <span className="w-2 h-2 bg-blue-600 rounded-full ml-2"></span>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Usuario */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{getUserDisplayName()}</p>
              <p className="text-xs text-gray-500">{user?.role_display || 'Usuario'}</p>
            </div>
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">{getUserInitials()}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
'use client';

import { 
  HomeIcon, 
  ChartBarIcon, 
  MapIcon, 
  ExclamationTriangleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  VideoCameraIcon
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/api';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const navigation = [
  { name: 'Vista General', href: 'overview', icon: HomeIcon },
  { name: 'Monitoreo en Tiempo Real', href: 'realtime', icon: VideoCameraIcon },
  { name: 'Infracciones', href: 'infractions', icon: ExclamationTriangleIcon },
  { name: 'Análisis', href: 'analytics', icon: ChartBarIcon },
  { name: 'Mapa', href: 'map', icon: MapIcon },
  { name: 'Configuración', href: 'settings', icon: Cog6ToothIcon },
];

export function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      // Limpiar todo el localStorage
      localStorage.clear();
      router.push('/login');
    }
  };

  return (
    <div className="flex flex-col w-64 bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="flex items-center h-16 px-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">Traffic Monitor</h1>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navigation.map((item) => (
          <button
            key={item.name}
            onClick={() => setActiveTab(item.href)}
            className={clsx(
              'w-full flex items-center px-3 py-2 text-sm font-medium rounded-md',
              activeTab === item.href
                ? 'bg-blue-100 text-blue-900'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            )}
          >
            <item.icon className="w-5 h-5 mr-3" />
            {item.name}
          </button>
        ))}
      </nav>
      
      {/* Footer with Logout */}
      <div className="px-4 py-4 border-t border-gray-200 space-y-2">
        <button
          onClick={handleLogout}
          className="w-full flex items-center px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-md"
        >
          <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
          Cerrar Sesión
        </button>
        <div className="text-xs text-gray-500 text-center">
          Sistema v1.0.0
        </div>
      </div>
    </div>
  );
}
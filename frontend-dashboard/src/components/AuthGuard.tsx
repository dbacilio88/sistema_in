'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Verificar autenticación
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    
    // Si no está autenticado y no está en login, redirigir
    if (!isAuthenticated && pathname !== '/login') {
      router.push('/login');
    }
    
    // Si está autenticado y está en login, redirigir al dashboard
    if (isAuthenticated && pathname === '/login') {
      router.push('/');
    }
  }, [pathname, router]);

  return <>{children}</>;
}

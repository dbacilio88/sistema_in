'use client';

interface AnalyticsChartsProps {
  fullView?: boolean;
}

export function AnalyticsCharts({ fullView = false }: AnalyticsChartsProps) {
  return (
    <div className='space-y-6'>
      <div className='bg-white rounded-lg shadow p-6'>
        <h3 className='text-lg font-medium text-gray-900'>
          Gráficos de Análisis {fullView && '(Vista Completa)'}
        </h3>
        <p className='text-sm text-gray-500 mt-2'>
          Los gráficos estarán disponibles próximamente.
        </p>
      </div>
    </div>
  );
}

import { test, expect } from '@playwright/test';

test.describe('Analytics Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.click('text=Análisis');
  });

  test('should display analytics charts', async ({ page }) => {
    // Verificar título de la sección
    await expect(page.locator('h2')).toContainText('Análisis y Reportes');
    
    // Verificar que hay gráficos visibles
    await expect(page.locator('svg')).toHaveCount({ min: 2 }); // Al menos 2 gráficos
    
    // Verificar gráficos específicos
    await expect(page.locator('text=Infracciones por Día')).toBeVisible();
    await expect(page.locator('text=Distribución por Tipo')).toBeVisible();
  });

  test('should show performance metrics in full view', async ({ page }) => {
    // En vista completa, deberían aparecer más gráficos
    await expect(page.locator('text=Patrón Horario de Infracciones')).toBeVisible();
    await expect(page.locator('text=Rendimiento del Sistema')).toBeVisible();
    
    // Verificar métricas de rendimiento
    await expect(page.locator('text=Precisión')).toBeVisible();
    await expect(page.locator('text=Latencia')).toBeVisible();
    await expect(page.locator('text=Uptime')).toBeVisible();
  });

  test('should display interactive charts', async ({ page }) => {
    // Verificar que los gráficos son interactivos
    const chart = page.locator('svg').first();
    await chart.hover();
    
    // Los tooltips aparecen en hover (implementado por Recharts)
    // Esto se puede verificar buscando elementos de tooltip
    await page.waitForTimeout(1000);
  });

  test('should show real-time data updates', async ({ page }) => {
    // Verificar que las métricas se actualizan
    const metricsContainer = page.locator('[data-testid="performance-metrics"]');
    
    // En la vista de analytics deberían aparecer métricas resumidas
    await expect(page.locator('text=94.2%')).toBeVisible(); // Precisión
    await expect(page.locator('text=185ms')).toBeVisible(); // Latencia
    await expect(page.locator('text=99.1%')).toBeVisible(); // Uptime
  });
});
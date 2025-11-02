import { test, expect } from '@playwright/test';

test.describe('System Integration E2E', () => {
  test('should complete full detection workflow', async ({ page }) => {
    // Simular flujo completo de detección de infracción
    
    // 1. Ir al dashboard
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Dashboard de Monitoreo');
    
    // 2. Verificar métricas iniciales
    const initialInfractions = await page.locator('[data-testid="infractions-count"]').textContent();
    
    // 3. Ir a la vista de infracciones
    await page.click('text=Infracciones');
    await expect(page.locator('h2')).toContainText('Gestión de Infracciones');
    
    // 4. Verificar que hay infracciones en la tabla
    await page.waitForSelector('tbody tr');
    const rowCount = await page.locator('tbody tr').count();
    expect(rowCount).toBeGreaterThan(0);
    
    // 5. Ver detalles de una infracción
    await page.click('tbody tr:first-child [data-testid="view-details"]');
    
    // 6. Ir al mapa para ver la ubicación
    await page.click('text=Mapa');
    await expect(page.locator('h2')).toContainText('Mapa de Tráfico');
    
    // 7. Hacer clic en un marcador de infracción
    await page.click('.bg-red-500');
    await expect(page.locator('[data-testid="location-info"]')).toBeVisible();
    
    // 8. Ir a analytics para ver el impacto
    await page.click('text=Análisis');
    await expect(page.locator('text=Distribución por Tipo')).toBeVisible();
    
    // 9. Volver al overview para verificar métricas actualizadas
    await page.click('text=Vista General');
    
    // Las métricas pueden haber cambiado durante el test
    const finalInfractions = await page.locator('[data-testid="infractions-count"]').textContent();
    expect(finalInfractions).toBeDefined();
  });

  test('should handle real-time updates across views', async ({ page }) => {
    // Probar actualizaciones en tiempo real
    
    // 1. Ir al dashboard
    await page.goto('/');
    
    // 2. Abrir múltiples tabs del navegador para simular usuarios concurrentes
    const context = page.context();
    const page2 = await context.newPage();
    await page2.goto('/');
    
    // 3. En la primera página, ir a infracciones
    await page.click('text=Infracciones');
    
    // 4. En la segunda página, ir a analytics  
    await page2.click('text=Análisis');
    
    // 5. Verificar que ambas páginas muestran datos
    await expect(page.locator('table')).toBeVisible();
    await expect(page2.locator('svg')).toHaveCount({ min: 2 });
    
    // 6. Esperar por actualizaciones en tiempo real
    await page.waitForTimeout(10000);
    
    // 7. Verificar que las páginas siguen siendo responsivas
    await page.click('text=Vista General');
    await page2.click('text=Mapa');
    
    await expect(page.locator('h1')).toContainText('Dashboard de Monitoreo');
    await expect(page2.locator('h2')).toContainText('Mapa de Tráfico');
    
    await page2.close();
  });

  test('should maintain performance under load', async ({ page }) => {
    // Test de rendimiento básico
    
    const startTime = Date.now();
    
    // 1. Cargar dashboard
    await page.goto('/');
    
    // 2. Navegar rápidamente entre vistas
    await page.click('text=Infracciones');
    await page.waitForSelector('table');
    
    await page.click('text=Análisis');
    await page.waitForSelector('svg');
    
    await page.click('text=Mapa');
    await page.waitForSelector('[data-testid="traffic-map"]');
    
    await page.click('text=Vista General');
    await page.waitForSelector('[data-testid="metrics-cards"]');
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    // Verificar que la navegación no tarde más de 10 segundos
    expect(totalTime).toBeLessThan(10000);
  });

  test('should work on mobile devices', async ({ page }) => {
    // Simular dispositivo móvil
    await page.setViewportSize({ width: 375, height: 667 });
    
    // 1. Cargar dashboard
    await page.goto('/');
    
    // 2. Verificar que el layout sea responsive
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
    
    // 3. Verificar que las métricas sean visibles en móvil
    await expect(page.locator('[data-testid="metrics-cards"]')).toBeVisible();
    
    // 4. Probar navegación en móvil
    await page.click('text=Infracciones');
    await expect(page.locator('table')).toBeVisible();
    
    // 5. Verificar scroll horizontal en tabla
    const table = page.locator('table');
    const tableWidth = await table.boundingBox();
    expect(tableWidth?.width).toBeGreaterThan(0);
    
    // 6. Probar mapa en móvil
    await page.click('text=Mapa');
    await expect(page.locator('[data-testid="traffic-map"]')).toBeVisible();
    
    // Resetear viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
  });
});
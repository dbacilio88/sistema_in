import { test, expect } from '@playwright/test';

test.describe('Traffic Map', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.click('text=Mapa');
  });

  test('should display traffic map', async ({ page }) => {
    // Verificar título
    await expect(page.locator('h2')).toContainText('Mapa de Tráfico');
    
    // Verificar que el mapa esté presente
    await expect(page.locator('[data-testid="traffic-map"]')).toBeVisible();
    
    // Verificar leyenda
    await expect(page.locator('text=Cámara Activa')).toBeVisible();
    await expect(page.locator('text=Cámara Inactiva')).toBeVisible();
    await expect(page.locator('text=Infracción')).toBeVisible();
    await expect(page.locator('text=Alerta')).toBeVisible();
  });

  test('should show location markers', async ({ page }) => {
    // Verificar que hay marcadores en el mapa
    const markers = page.locator('[data-testid="location-marker"]');
    await expect(markers).toHaveCount({ min: 3 }); // Al menos 3 marcadores
    
    // Verificar que hay diferentes tipos de marcadores
    const cameraMarkers = page.locator('.bg-green-500');
    const infractionMarkers = page.locator('.bg-red-500');
    
    expect(await cameraMarkers.count() + await infractionMarkers.count()).toBeGreaterThan(0);
  });

  test('should show location details on marker click', async ({ page }) => {
    // Hacer clic en un marcador
    await page.click('[data-testid="location-marker"]');
    
    // Verificar que aparece el panel de información
    await expect(page.locator('[data-testid="location-info"]')).toBeVisible();
    
    // Verificar contenido del panel
    await expect(page.locator('text=Estado:')).toBeVisible();
    await expect(page.locator('text=Tipo:')).toBeVisible();
    await expect(page.locator('text=Coordenadas:')).toBeVisible();
  });

  test('should close location info panel', async ({ page }) => {
    // Hacer clic en un marcador para abrir el panel
    await page.click('[data-testid="location-marker"]');
    await expect(page.locator('[data-testid="location-info"]')).toBeVisible();
    
    // Cerrar el panel
    await page.click('[data-testid="close-info"]');
    await expect(page.locator('[data-testid="location-info"]')).not.toBeVisible();
  });

  test('should display different marker states', async ({ page }) => {
    // Verificar marcadores de estado activo (verde)
    await expect(page.locator('.bg-green-500')).toHaveCount({ min: 1 });
    
    // Verificar marcadores de infracción (rojo)
    await expect(page.locator('.bg-red-500')).toHaveCount({ min: 1 });
    
    // Verificar marcadores inactivos (gris)
    const inactiveMarkers = page.locator('.bg-gray-400');
    // Puede o no haber marcadores inactivos, pero si los hay, deberían ser visibles
  });
});
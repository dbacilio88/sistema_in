import { defineConfig, devices } from '@playwright/test';
import { config } from 'dotenv';

// Cargar variables de entorno
config();

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Directorio de tests
  testDir: './e2e',
  
  // Tiempo máximo por test
  timeout: 30 * 1000,
  
  // Tiempo máximo para expect()
  expect: {
    timeout: 5000,
  },
  
  // Configuración para CI
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  // Reporters
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }],
  ],
  
  // Configuración global
  use: {
    // URL base para todos los tests
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    // Configuración de trazas para debugging
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Configuración del navegador
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // Configuración de proyectos (navegadores)
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // Tests móviles
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Servidor de desarrollo local
  webServer: [
    {
      command: 'cd ../frontend-dashboard && npm run dev',
      port: 3000,
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
    {
      command: 'cd ../backend-django && python manage.py runserver 8000',
      port: 8000,
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
    {
      command: 'cd ../inference-service && uvicorn app.main:app --host 0.0.0.0 --port 8001',
      port: 8001,
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    }
  ],
});
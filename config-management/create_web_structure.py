"""
Interfaz web para gestión de configuración
==========================================

Interfaz web moderna para administrar la configuración del sistema de 
detección de infracciones con React y TypeScript.
"""

import json
from pathlib import Path

# Crear estructura de directorios para la interfaz web
web_structure = {
    "public/index.html": """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sistema de Configuración - Traffic Detection</title>
  <link rel="icon" type="image/svg+xml" href="/vite.svg" />
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>""",

    "src/main.tsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",

    "src/App.tsx": """import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider } from './contexts/ConfigContext'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import SystemConfig from './pages/SystemConfig'
import CamerasConfig from './pages/CamerasConfig'
import MLModelsConfig from './pages/MLModelsConfig'
import DetectionConfig from './pages/DetectionConfig'
import ImportExport from './pages/ImportExport'
import Login from './pages/Login'
import ProtectedRoute from './components/ProtectedRoute'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <ConfigProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/system" element={<SystemConfig />} />
                        <Route path="/cameras" element={<CamerasConfig />} />
                        <Route path="/models" element={<MLModelsConfig />} />
                        <Route path="/detection" element={<DetectionConfig />} />
                        <Route path="/import-export" element={<ImportExport />} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </div>
        </Router>
      </ConfigProvider>
    </AuthProvider>
  )
}

export default App""",

    "src/index.css": """@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

#root {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.App {
  width: 100vw;
  height: 100vh;
}""",

    "src/App.css": """.app-container {
  min-height: 100vh;
  background-color: #f8fafc;
}

.content-area {
  padding: 1rem;
}

@media (min-width: 768px) {
  .content-area {
    padding: 2rem;
  }
}""",

    "package.json": json.dumps({
        "name": "config-management-web",
        "private": True,
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "tsc && vite build",
            "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.8.1",
            "axios": "^1.3.4",
            "react-hook-form": "^7.43.5",
            "react-hot-toast": "^2.4.0",
            "lucide-react": "^0.321.0",
            "recharts": "^2.5.0",
            "leaflet": "^1.9.3",
            "react-leaflet": "^4.2.1",
            "@headlessui/react": "^1.7.13",
            "clsx": "^1.2.1",
            "date-fns": "^2.29.3"
        },
        "devDependencies": {
            "@types/react": "^18.0.28",
            "@types/react-dom": "^18.0.11",
            "@types/leaflet": "^1.9.3",
            "@typescript-eslint/eslint-plugin": "^5.57.1",
            "@typescript-eslint/parser": "^5.57.1",
            "@vitejs/plugin-react": "^4.0.0",
            "autoprefixer": "^10.4.14",
            "eslint": "^8.38.0",
            "eslint-plugin-react-hooks": "^4.6.0",
            "eslint-plugin-react-refresh": "^0.3.4",
            "postcss": "^8.4.21",
            "tailwindcss": "^3.2.7",
            "typescript": "^5.0.2",
            "vite": "^4.3.2"
        }
    }, indent=2),

    "vite.config.ts": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})""",

    "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}""",

    "postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}""",

    "tsconfig.json": json.dumps({
        "compilerOptions": {
            "target": "ES2020",
            "useDefineForClassFields": True,
            "lib": ["ES2020", "DOM", "DOM.Iterable"],
            "module": "ESNext",
            "skipLibCheck": True,
            "moduleResolution": "bundler",
            "allowImportingTsExtensions": True,
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True,
            "jsx": "react-jsx",
            "strict": True,
            "noUnusedLocals": True,
            "noUnusedParameters": True,
            "noFallthroughCasesInSwitch": True
        },
        "include": ["src"],
        "references": [{"path": "./tsconfig.node.json"}]
    }, indent=2),

    "tsconfig.node.json": json.dumps({
        "compilerOptions": {
            "composite": True,
            "skipLibCheck": True,
            "module": "ESNext",
            "moduleResolution": "bundler",
            "allowSyntheticDefaultImports": True
        },
        "include": ["vite.config.ts"]
    }, indent=2)
}

def create_web_interface():
    """Crear la estructura de la interfaz web"""
    base_dir = Path("web")
    base_dir.mkdir(exist_ok=True)
    
    for file_path, content in web_structure.items():
        full_path = base_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ Estructura web creada en {base_dir}")

if __name__ == "__main__":
    create_web_interface()
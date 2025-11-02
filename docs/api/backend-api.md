# API REST Backend - Documentación Completa

## Información General

### Base URL
- **Desarrollo**: `http://localhost:8000/api/v1`
- **Staging**: `https://staging-api.trafficsystem.com/api/v1`
- **Producción**: `https://api.trafficsystem.com/api/v1`

### Autenticación
El sistema utiliza autenticación basada en JWT (JSON Web Tokens).

```http
Authorization: Bearer <jwt_token>
```

### Formato de Respuesta
Todas las respuestas siguen el formato estándar:

```json
{
  "success": true|false,
  "data": <response_data>,
  "message": "Mensaje descriptivo",
  "errors": <array_of_errors>,
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

## Autenticación

### POST /auth/login
Autenticar usuario y obtener token JWT.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "permissions": ["read", "write", "admin"]
    }
  }
}
```

### POST /auth/refresh
Renovar token de acceso usando refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### POST /auth/logout
Cerrar sesión e invalidar tokens.

**Headers:** `Authorization: Bearer <token>`

## Gestión de Usuarios

### GET /users
Listar usuarios del sistema.

**Query Parameters:**
- `page` (integer): Número de página (default: 1)
- `per_page` (integer): Elementos por página (default: 20, max: 100)
- `search` (string): Buscar por nombre o email
- `role` (string): Filtrar por rol (admin, operator, viewer)
- `active` (boolean): Filtrar por estado activo

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User",
      "role": "admin",
      "is_active": true,
      "last_login": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

### POST /users
Crear nuevo usuario.

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "admin|operator|viewer"
}
```

### GET /users/{id}
Obtener detalles de un usuario específico.

### PUT /users/{id}
Actualizar información de usuario.

### DELETE /users/{id}
Eliminar usuario (soft delete).

## Gestión de Vehículos

### GET /vehicles
Listar vehículos registrados.

**Query Parameters:**
- `page`, `per_page`: Paginación
- `search`: Buscar por placa, marca, modelo
- `type`: Filtrar por tipo (car, truck, motorcycle, bus)
- `status`: Filtrar por estado (active, inactive, suspended)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "license_plate": "ABC123",
      "make": "Toyota",
      "model": "Corolla",
      "year": 2020,
      "color": "Blanco",
      "type": "car",
      "owner": {
        "id": 1,
        "name": "Juan Pérez",
        "document": "12345678"
      },
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST /vehicles
Registrar nuevo vehículo.

**Request:**
```json
{
  "license_plate": "string",
  "make": "string",
  "model": "string",
  "year": "integer",
  "color": "string",
  "type": "car|truck|motorcycle|bus",
  "owner_id": "integer"
}
```

### GET /vehicles/{id}
Obtener detalles de un vehículo.

### PUT /vehicles/{id}
Actualizar información de vehículo.

### DELETE /vehicles/{id}
Eliminar vehículo.

## Gestión de Infracciones

### GET /infractions
Listar infracciones detectadas.

**Query Parameters:**
- `page`, `per_page`: Paginación
- `status`: Filtrar por estado (pending, confirmed, dismissed, paid)
- `type`: Filtrar por tipo de infracción
- `date_from`, `date_to`: Rango de fechas
- `location`: Filtrar por ubicación
- `license_plate`: Filtrar por placa

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "type": "speeding",
      "description": "Exceso de velocidad",
      "location": {
        "latitude": -12.0464,
        "longitude": -77.0428,
        "address": "Av. Javier Prado 123, Lima"
      },
      "timestamp": "2024-01-15T14:30:00Z",
      "vehicle": {
        "id": 1,
        "license_plate": "ABC123",
        "make": "Toyota",
        "model": "Corolla"
      },
      "evidence": [
        {
          "type": "image",
          "url": "/media/infractions/2024/01/15/evidence_1.jpg",
          "timestamp": "2024-01-15T14:30:00Z"
        }
      ],
      "fine_amount": 150.00,
      "status": "pending",
      "confidence_score": 0.95,
      "created_at": "2024-01-15T14:31:00Z"
    }
  ]
}
```

### POST /infractions
Crear nueva infracción (manual).

**Request:**
```json
{
  "type": "string",
  "description": "string",
  "location": {
    "latitude": "float",
    "longitude": "float",
    "address": "string"
  },
  "vehicle_id": "integer",
  "evidence_files": ["file_id_1", "file_id_2"],
  "fine_amount": "decimal",
  "notes": "string"
}
```

### GET /infractions/{id}
Obtener detalles de una infracción.

### PUT /infractions/{id}
Actualizar infracción.

**Request:**
```json
{
  "status": "confirmed|dismissed|paid",
  "notes": "string",
  "fine_amount": "decimal"
}
```

### POST /infractions/{id}/confirm
Confirmar infracción.

### POST /infractions/{id}/dismiss
Desestimar infracción.

### POST /infractions/{id}/pay
Marcar infracción como pagada.

## Detección de Infracciones

### POST /detection/analyze
Analizar imagen/video para detectar infracciones.

**Request (multipart/form-data):**
```
file: <image_or_video_file>
location_latitude: float
location_longitude: float
camera_id: string (optional)
timestamp: datetime (optional)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "detections": [
      {
        "vehicle": {
          "license_plate": "ABC123",
          "confidence": 0.98,
          "bbox": [100, 50, 200, 150]
        },
        "infractions": [
          {
            "type": "speeding",
            "confidence": 0.95,
            "evidence": {
              "speed_detected": 80,
              "speed_limit": 60
            }
          }
        ]
      }
    ],
    "processing_time": 2.5,
    "timestamp": "2024-01-15T14:30:00Z"
  }
}
```

### GET /detection/cameras
Listar cámaras de detección.

### POST /detection/cameras
Registrar nueva cámara.

### GET /detection/statistics
Obtener estadísticas de detección.

## Dispositivos de Monitoreo

### GET /devices
Listar dispositivos registrados.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Cámara Av. Principal",
      "type": "camera",
      "location": {
        "latitude": -12.0464,
        "longitude": -77.0428,
        "address": "Av. Principal 123"
      },
      "status": "online",
      "last_heartbeat": "2024-01-15T14:30:00Z",
      "configuration": {
        "resolution": "1920x1080",
        "fps": 30,
        "detection_zones": []
      }
    }
  ]
}
```

### POST /devices
Registrar nuevo dispositivo.

### GET /devices/{id}/status
Obtener estado de dispositivo.

### PUT /devices/{id}/configuration
Actualizar configuración de dispositivo.

## Reportes y Estadísticas

### GET /reports/infractions
Generar reporte de infracciones.

**Query Parameters:**
- `date_from`, `date_to`: Rango de fechas
- `group_by`: day|week|month|location|type
- `format`: json|csv|pdf

### GET /reports/vehicles
Reporte de vehículos.

### GET /reports/revenue
Reporte de ingresos por multas.

### GET /statistics/dashboard
Estadísticas para dashboard principal.

**Response:**
```json
{
  "success": true,
  "data": {
    "infractions": {
      "total": 1250,
      "today": 45,
      "pending": 120,
      "confirmed": 980,
      "dismissed": 150
    },
    "vehicles": {
      "total": 5800,
      "active": 5600,
      "suspended": 200
    },
    "revenue": {
      "total": 187500.00,
      "this_month": 25000.00,
      "pending": 18000.00
    },
    "detection_accuracy": 0.94
  }
}
```

## Configuración del Sistema

### GET /config
Obtener configuración del sistema.

### PUT /config
Actualizar configuración.

**Request:**
```json
{
  "detection": {
    "confidence_threshold": 0.8,
    "auto_confirm_threshold": 0.95
  },
  "fines": {
    "speeding": 150.00,
    "red_light": 200.00,
    "parking": 80.00
  },
  "notifications": {
    "email_enabled": true,
    "sms_enabled": false
  }
}
```

## WebSocket Events

### /ws/infractions
Stream en tiempo real de nuevas infracciones.

**Events:**
- `infraction.created`: Nueva infracción detectada
- `infraction.updated`: Infracción actualizada
- `infraction.confirmed`: Infracción confirmada

### /ws/devices
Estado en tiempo real de dispositivos.

**Events:**
- `device.online`: Dispositivo conectado
- `device.offline`: Dispositivo desconectado
- `device.alert`: Alerta de dispositivo

## Códigos de Error

### 400 Bad Request
```json
{
  "success": false,
  "message": "Datos de entrada inválidos",
  "errors": [
    {
      "field": "email",
      "message": "Formato de email inválido"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Token de autenticación requerido o inválido"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "message": "No tiene permisos para realizar esta acción"
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "Recurso no encontrado"
}
```

### 422 Validation Error
```json
{
  "success": false,
  "message": "Error de validación",
  "errors": [
    {
      "field": "license_plate",
      "message": "La placa ya está registrada"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Error interno del servidor"
}
```

## Rate Limiting

- **Límite por defecto**: 1000 requests/hora por IP
- **Límite autenticado**: 5000 requests/hora por usuario
- **Headers de respuesta**:
  - `X-RateLimit-Limit`: Límite total
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Reset`: Timestamp de reset

## Versionado de API

- **Versión actual**: v1
- **Header**: `Accept: application/vnd.trafficsystem.v1+json`
- **URL**: `/api/v1/`

## Testing

### Postman Collection
Importar la colección: [postman-collection.json](postman-collection.json)

### cURL Examples

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Lista de infracciones:**
```bash
curl -X GET http://localhost:8000/api/v1/infractions \
  -H "Authorization: Bearer <token>"
```

## SDK y Librerías Cliente

- **Python**: `pip install trafficsystem-client`
- **JavaScript**: `npm install trafficsystem-client`
- **PHP**: `composer require trafficsystem/client`

### Ejemplo Python
```python
from trafficsystem_client import TrafficSystemClient

client = TrafficSystemClient(
    base_url="http://localhost:8000/api/v1",
    token="your_jwt_token"
)

# Listar infracciones
infractions = client.infractions.list()

# Crear infracción
infraction = client.infractions.create({
    "type": "speeding",
    "vehicle_id": 1,
    "location": {"latitude": -12.0464, "longitude": -77.0428}
})
```
# Credenciales de Prueba - Sistema de Tráfico

## Usuario Administrador

**Opción 1: Login con Username**
- Username: `admin`
- Password: `admin123`

**Opción 2: Login con Email**
- Email: `admin@traffic.local`
- Password: `admin123`

## URLs del Sistema

- **Frontend Dashboard**: http://localhost:3002
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Health Check**: http://localhost:8000/api/health/
- **API Login**: http://localhost:8000/api/auth/login/

## Endpoints de API

### Autenticación
- **POST** `/api/auth/login/` - Login con username o email
- **POST** `/api/auth/register/` - Registro de usuario
- **GET** `/api/auth/users/me/` - Perfil del usuario actual
- **PUT** `/api/auth/users/me/` - Actualizar perfil

### Notificaciones
- **GET** `/api/notifications/` - Lista de notificaciones
- **GET** `/api/notifications/unread/` - Notificaciones no leídas
- **PUT** `/api/notifications/{id}/mark-as-read/` - Marcar como leída
- **POST** `/api/notifications/mark-all-read/` - Marcar todas como leídas

### Vehículos
- **GET** `/api/vehicles/` - Lista de vehículos
- **POST** `/api/vehicles/` - Crear vehículo
- **GET** `/api/vehicles/{id}/` - Detalle de vehículo
- **PUT** `/api/vehicles/{id}/` - Actualizar vehículo
- **DELETE** `/api/vehicles/{id}/` - Eliminar vehículo

### Dispositivos
- **GET** `/api/devices/` - Lista de dispositivos
- **POST** `/api/devices/` - Crear dispositivo
- **GET** `/api/devices/{id}/` - Detalle de dispositivo

### Infracciones
- **GET** `/api/infractions/` - Lista de infracciones
- **GET** `/api/infractions/{id}/` - Detalle de infracción

## Ejemplo de Login con cURL

```bash
# Login con username
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Login con email
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@traffic.local","password":"admin123"}'
```

## Respuesta de Login Exitoso

```json
{
  "success": true,
  "data": {
    "refresh": "eyJ...",
    "access": "eyJ...",
    "user": {
      "id": "cb34186f-a903-4107-b481-148e65a035a6",
      "username": "admin",
      "email": "admin@traffic.local",
      "role": "admin",
      "is_active": true,
      "is_staff": true
    }
  }
}
```

## Uso del Token

Para hacer peticiones autenticadas, incluye el token de acceso en el header:

```bash
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Notas Importantes

1. El sistema acepta tanto **username** como **email** para el login
2. Los tokens JWT tienen una duración de 1 hora (access) y 7 días (refresh)
3. El usuario admin tiene permisos completos en el sistema
4. La API está protegida con autenticación JWT
5. El frontend redirecciona automáticamente al login si no estás autenticado

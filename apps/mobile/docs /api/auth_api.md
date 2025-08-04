# Documentación API de Autenticación

Esta documentación detalla todos los endpoints relacionados con la autenticación de usuarios en FitCoach AI.

## Índice
- [Registro de Usuario](#registro-de-usuario)
- [Inicio de Sesión](#inicio-de-sesión)
- [Actualización de Token](#actualización-de-token)
- [Cierre de Sesión](#cierre-de-sesión)
- [Verificación de Email](#verificación-de-email)
- [Reenvío de Verificación](#reenvío-de-verificación)
- [Recuperación de Contraseña](#recuperación-de-contraseña)
- [Verificación de Token de Recuperación](#verificación-de-token-de-recuperación)
- [Cambio de Contraseña](#cambio-de-contraseña)

## Registro de Usuario

**Endpoint:** `POST /auth/register`

Registra un nuevo usuario en el sistema y envía un email de verificación.

### Petición

```json
{
  "username": "usuario123",
  "email": "usuario@ejemplo.com",
  "password": "Contraseña123"
}
```

#### Validaciones
- Username: Requerido
- Email: Debe ser un email válido
- Password: 
  - Mínimo 8 caracteres
  - Debe contener al menos un número
- Full name: Opcional

### Respuesta Exitosa (200)

```json
{
  "id": 1,
  "username": "usuario123",
  "email": "usuario@ejemplo.com",
  "full_name": "Nombre Completo",
  "is_active": true,
  "created_at": "2024-03-19T10:00:00Z",
  "updated_at": null
}
```

### Errores Posibles
- `400`: Datos de registro inválidos
- `409`: Email o username ya existen
- `500`: Error interno del servidor

## Inicio de Sesión

**Endpoint:** `POST /auth/login`

Autentica un usuario y devuelve tokens de acceso y actualización.

### Petición
```json
{
  "username": "usuario123",
  "password": "Contraseña123"
}
```

### Respuesta Exitosa (200)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Errores Posibles
- `401`: Credenciales inválidas
- `403`: Cuenta no verificada
- `500`: Error interno del servidor

## Actualización de Token

**Endpoint:** `POST /auth/refresh`

Renueva los tokens de acceso y actualización usando un refresh token válido.

### Petición
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Respuesta Exitosa (200)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Errores Posibles
- `401`: Token de actualización inválido o expirado
- `500`: Error interno del servidor

## Cierre de Sesión

**Endpoint:** `POST /auth/logout`

Revoca los tokens de acceso y actualización del usuario.

### Petición
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Headers Requeridos
```
Authorization: Bearer <access_token>
```

### Respuesta Exitosa (200)
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

### Errores Posibles
- `401`: Token inválido o expirado
- `500`: Error interno del servidor

## Verificación de Email

**Endpoint:** `POST /auth/verify-email` o `GET /auth/verify-email`

Verifica el email de un usuario usando el token enviado por correo.

### Parámetros de Query
- `token`: Token de verificación recibido por email

### Respuesta Exitosa (200)
```json
{
  "message": "Email verificado exitosamente"
}
```

### Errores Posibles
- `400`: Token inválido
- `410`: Token expirado
- `500`: Error interno del servidor

## Reenvío de Verificación

**Endpoint:** `POST /auth/resend-verification`

Reenvía el email de verificación a un usuario no verificado.

### Petición
```json
{
  "email": "usuario@ejemplo.com"
}
```

### Respuesta Exitosa (200)
```json
{
  "message": "Email de verificación reenviado"
}
```

### Errores Posibles
- `400`: Email no encontrado
- `409`: Email ya verificado
- `500`: Error interno del servidor

## Recuperación de Contraseña

**Endpoint:** `POST /auth/forgot-password`

Inicia el proceso de recuperación de contraseña enviando un email con instrucciones.

### Petición
```json
{
  "email": "usuario@ejemplo.com"
}
```

### Respuesta Exitosa (200)
```json
{
  "message": "Si el email existe, recibirás instrucciones para restablecer tu contraseña"
}
```

### Errores Posibles
- `500`: Error interno del servidor

## Verificación de Token de Recuperación

**Endpoint:** `GET /auth/reset-password/verify`

Verifica si un token de recuperación de contraseña es válido.

### Parámetros de Query
- `token`: Token de recuperación recibido por email

### Respuesta Exitosa (200)
```json
{
  "message": "Token válido"
}
```

### Errores Posibles
- `400`: Token inválido
- `410`: Token expirado
- `500`: Error interno del servidor

## Cambio de Contraseña

**Endpoint:** `POST /auth/reset-password`

Cambia la contraseña de un usuario usando un token de recuperación válido.

### Petición
```json
{
  "token": "token-de-recuperacion",
  "new_password": "NuevaContraseña123",
  "confirm_password": "NuevaContraseña123"
}
```

### Validaciones de Contraseña
- Mínimo 8 caracteres
- Debe contener al menos un número
- Las contraseñas deben coincidir

### Respuesta Exitosa (200)
```json
{
  "message": "Contraseña actualizada exitosamente"
}
```

### Errores Posibles
- `400`: Token inválido o contraseñas no coinciden
- `410`: Token expirado
- `500`: Error interno del servidor 
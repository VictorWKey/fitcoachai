# Endpoints de Desarrollo

Este documento describe los endpoints creados específicamente para desarrollo y testing cuando no hay servicio SMTP disponible.

## Verificación Directa de Usuario

**Endpoint:** `POST /auth/verify-user-direct`

Verifica directamente un usuario por email sin necesidad de token SMTP.

### Petición
```json
{
  "email": "usuario@ejemplo.com"
}
```

### Respuesta Exitosa (200)
```json
{
  "message": "Usuario usuario@ejemplo.com verificado exitosamente"
}
```

### Respuestas Adicionales
- **200**: Si el usuario ya está verificado
```json
{
  "message": "El usuario usuario@ejemplo.com ya está verificado"
}
```

### Errores Posibles
- **404**: Usuario no encontrado
```json
{
  "detail": "Usuario no encontrado"
}
```
- **500**: Error interno del servidor

## Lista de Usuarios No Verificados

**Endpoint:** `GET /auth/unverified-users`

Lista todos los usuarios que aún no han verificado su email.

### Respuesta Exitosa (200)
```json
{
  "count": 2,
  "users": [
    {
      "id": 1,
      "username": "usuario1",
      "email": "usuario1@ejemplo.com",
      "created_at": "2025-08-05T10:30:00Z",
      "verification_token_expires": "2025-08-06T10:30:00Z"
    },
    {
      "id": 2,
      "username": "usuario2",
      "email": "usuario2@ejemplo.com",
      "created_at": "2025-08-05T11:00:00Z",
      "verification_token_expires": "2025-08-06T11:00:00Z"
    }
  ]
}
```

### Errores Posibles
- **500**: Error interno del servidor

## Uso Recomendado

### 1. Flujo de Desarrollo Típico

1. **Registrar un usuario** usando `POST /auth/register`
2. **Listar usuarios no verificados** usando `GET /auth/unverified-users`
3. **Verificar usuario directamente** usando `POST /auth/verify-user-direct`
4. **Hacer login** usando `POST /auth/login`

### 2. Ejemplo con cURL

```bash
# 1. Registrar usuario
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# 2. Ver usuarios no verificados
curl -X GET "http://localhost:8000/auth/unverified-users"

# 3. Verificar usuario directamente
curl -X POST "http://localhost:8000/auth/verify-user-direct" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'

# 4. Hacer login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

### 3. Ejemplo con Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Registrar usuario
register_data = {
    "username": "testuser",
    "email": "test@example.com", 
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("Registro:", response.json())

# Ver usuarios no verificados
response = requests.get(f"{BASE_URL}/auth/unverified-users")
print("Usuarios no verificados:", response.json())

# Verificar usuario
verify_data = {"email": "test@example.com"}
response = requests.post(f"{BASE_URL}/auth/verify-user-direct", json=verify_data)
print("Verificación:", response.json())

# Login
login_data = {"username": "test@example.com", "password": "password123"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
print("Login:", response.json())
```

## Notas Importantes

⚠️ **Solo para Desarrollo**: Estos endpoints están destinados únicamente para desarrollo y testing. No deben usarse en producción.

⚠️ **Seguridad**: En producción, la verificación por email es esencial para la seguridad. Estos endpoints omiten esta verificación importante.

⚠️ **Limpieza**: Considera agregar autenticación admin a estos endpoints si planeas mantenerlos más allá del desarrollo inicial.

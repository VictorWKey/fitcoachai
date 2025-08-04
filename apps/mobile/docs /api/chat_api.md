# Documentación API de Chat

Esta documentación detalla todos los endpoints relacionados con el chat y la interacción con el agente de IA en FitCoach AI.

## Índice
- [Enviar Mensaje](#enviar-mensaje)
- [Obtener Historial](#obtener-historial)
- [Eliminar Memoria](#eliminar-memoria)

## Enviar Mensaje

**Endpoint:** `POST /chat/`

Envía un mensaje al agente de IA y recibe una respuesta. El sistema procesa el mensaje a través del agente LLM y almacena tanto el mensaje del usuario como la respuesta del asistente en el historial.

### Headers Requeridos
```
Authorization: Bearer <access_token>
```

### Petición
```json
{
  "input": "¿Cuál es mi rutina de ejercicios para hoy?"
}
```

### Respuesta Exitosa (200)
```json
{
  "id": 124,
  "role": "assistant",
  "content": "Basado en tu plan de entrenamiento, hoy tienes programado...",
  "created_at": "2024-03-19T10:00:01Z"
}
```

### Errores Posibles
- `401`: Token de acceso inválido o expirado
- `403`: Usuario no verificado
- `500`: Error interno del servidor

## Obtener Historial

**Endpoint:** `GET /chat/history`

Recupera el historial de conversaciones del usuario con el agente de IA.

### Headers Requeridos
```
Authorization: Bearer <access_token>
```

### Parámetros de Query
- `after_id` (opcional): ID del último mensaje recibido (para carga incremental). Default: 0
- `limit` (opcional): Número máximo de mensajes a retornar. Default: 50, Max: 100

### Respuesta Exitosa (200)
```json
[
  {
    "id": 123,
    "role": "user",
    "content": "¿Cuál es mi rutina de ejercicios para hoy?",
    "created_at": "2024-03-19T10:00:00Z"
  },
  {
    "id": 124,
    "role": "assistant",
    "content": "Basado en tu plan de entrenamiento, hoy tienes programado...",
    "created_at": "2024-03-19T10:00:01Z"
  }
]
```

### Errores Posibles
- `401`: Token de acceso inválido o expirado
- `403`: Usuario no verificado
- `400`: Parámetros de query inválidos
- `500`: Error interno del servidor

## Eliminar Memoria

**Endpoint:** `DELETE /chat/delete-memory`

Elimina toda la memoria de conversación del agente para el usuario actual. Esto puede ser útil si deseas que el agente "olvide" el contexto previo.

### Headers Requeridos
```
Authorization: Bearer <access_token>
```

### Respuesta Exitosa (200)
```json
{
  "message": "Memory deleted successfully"
}
```

### Errores Posibles
- `401`: Token de acceso inválido o expirado
- `403`: Usuario no verificado
- `500`: Error interno del servidor 
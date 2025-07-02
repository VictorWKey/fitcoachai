# FitCoach AI 🏋️‍♀️

**FitCoach AI** es una aplicación de entrenamiento personal impulsada por inteligencia artificial que proporciona coaching personalizado y seguimiento detallado de ejercicios. Utiliza un agente LLM avanzado construido con LangGraph para ofrecer recomendaciones de entrenamiento inteligentes y análisis de rendimiento.

## 🚀 Características Principales

- **Coaching con IA**: Agente conversacional inteligente que proporciona recomendaciones personalizadas
- **Seguimiento Multi-Disciplinario**: Soporte para 9 disciplinas de fitness diferentes
- **Análisis de Rendimiento**: Métricas detalladas y seguimiento de progreso
- **API RESTful**: Arquitectura moderna y escalable
- **Sistema de Cache LRU**: Optimización de rendimiento para respuestas rápidas
- **Autenticación Segura**: Sistema robusto con JWT y protección CSRF

## 🏃‍♀️ Disciplinas de Fitness Soportadas

### 1. **Hipertrofia (Bodybuilding/Fitness)**
Enfocada en el crecimiento muscular y desarrollo estético.
- **Propiedades específicas:**
  - **Repeticiones objetivo y completadas**: Números enteros
  - **Peso y unidad**: Valor numérico + unidad (`kg`, `lb`)
  - **RPE** (Rate of Perceived Exertion): `1-10` escala
  - **RIR** (Reps in Reserve): `0-10+` repeticiones en reserva
  - **Tempo de movimiento**: Segundos por fase
    - Excéntrico, Pausa inferior, Concéntrico
  - **Tiempo de descanso**: Segundos entre series
  - **Rango de movimiento**: `full`, `partial_top`, `partial_bottom`, `quarter`, `half`
  - **Músculo objetivo**: Texto libre
  - **Notas adicionales**: Texto libre

### 2. **Fuerza Máxima (Powerlifting/Olympic)**
Entrenamiento para desarrollar la máxima capacidad de fuerza.
- **Propiedades específicas:**
  - **Repeticiones y peso levantado**: Números enteros y valor numérico
  - **Unidad de peso**: `kg`, `lb`
  - **RPE** (Rate of Perceived Exertion): `1-10` escala
  - **RIR** (Reps in Reserve): `0-10+` repeticiones en reserva
  - **Tiempo de descanso**: `30-1200+` segundos
  - **Porcentaje de 1RM**: `30-120%` del máximo
  - **Tempo de movimiento**: Segundos por fase
    - Excéntrico, Pausa inferior, Concéntrico
  - **Tipo de ejercicio**: `squat`, `bench`, `deadlift`, etc.

### 3. **Potencia (Pliometría/Sprints/Halterofilia)**
Desarrollo de la capacidad explosiva y velocidad.
- **Propiedades específicas:**
  - **Altura de salto**: Centímetros (valor decimal)
  - **Distancia de salto**: Centímetros (valor decimal)
  - **Tiempo de contacto con el suelo**: Milisegundos (valor decimal)
  - **Fuerza de impacto**: Múltiplos del peso corporal (valor decimal)
  - **Velocidad máxima**: km/h (valor decimal)
  - **Tiempo de aceleración**: Segundos (valor decimal)
  - **Potencia pico**: Watts (valor decimal)
  - **Tiempo de recuperación**: Segundos (entero)

### 4. **Resistencia (Running/Cycling/Rowing)**
Entrenamiento cardiovascular de larga duración.
- **Propiedades específicas:**
  - **Tipo de actividad**: `running`, `cycling`, `rowing`
  - **Distancia total**: Valor numérico
  - **Unidad de distancia**: `km`, `mi`, `m`
  - **Duración**: Segundos (entero)
  - **Ritmo promedio**: Segundos por km (entero)
  - **Velocidad promedio**: km/h (valor decimal)
  - **Frecuencia cardíaca promedio y máxima**: bpm (enteros)
  - **Zonas de frecuencia cardíaca**: String JSON con porcentajes por zona
  - **Cadencia**: `steps/min`, `rpm`, `strokes/min` (entero)
  - **Ganancia de elevación**: Metros (valor decimal)
  - **Potencia promedio y máxima**: Watts (valor decimal)
  - **Esfuerzo percibido**: `1-10` escala
  - **Tiempos parciales**: String JSON con tiempos por segmento
  - **Condiciones climáticas**: Texto libre
  - **Temperatura**: Celsius (valor decimal)

### 5. **Cardio (HIIT/LISS/Spinning)**
Entrenamiento cardiovascular estructurado con intervalos.
- **Propiedades específicas:**
  - **Tipo de cardio**: `HIIT`, `LISS`, `spinning`
  - **Duración total**: Segundos (entero)
  - **Intervalos completados**: Número entero
  - **Relación trabajo:descanso**: Texto (`"1:1"`, `"1:2"`, `"3:1"`, etc.)
  - **Frecuencia cardíaca promedio y máxima**: bpm (enteros)
  - **Zonas de frecuencia cardíaca**: String JSON
  - **Calorías estimadas**: Número entero
  - **Potencia promedio y máxima**: Watts (valor decimal)
  - **RPE promedio**: `1-10` escala
  - **Cadencia promedio**: Número entero
  - **Nivel de resistencia**: `0-100` escala
  - **Velocidad promedio**: km/h (valor decimal)
  - **Datos de RPE por intervalo**: String JSON con RPE por intervalo

### 6. **Flexibilidad (Stretching/Yoga)**
Mejora de la movilidad y flexibilidad articular.
- **Propiedades específicas:**
  - **Nombre del ejercicio**: Texto libre
  - **Articulación**: Texto libre
  - **Rango de movimiento**: `0-360` grados (valor decimal)
  - **Tiempo de estiramiento**: Segundos (entero)
  - **Escala de intensidad**: `1-10` escala
  - **Tipo de estiramiento**: `static`, `dynamic`, `pnf`, `ballistic`
  - **Nivel de dolor**: `0-10` escala
  - **Sensación pre y post sesión**: Texto libre
  - **Porcentaje de mejora**: `-90%` a `+500%` (valor decimal)
  - **Temperatura ambiente**: Celsius (valor decimal)
  - **Sensación de temperatura corporal**: `cold`, `warm`, `hot`

### 7. **Equilibrio (Bosu/Slackline/Yoga)**
Desarrollo del control postural y estabilidad.
- **Propiedades específicas:**
  - **Tiempo de mantenimiento**: Segundos (entero)
  - **Intentos para lograr la posición**: Número entero
  - **Amplitud de oscilación**: Grados (valor decimal)
  - **Tiempo de recuperación**: Segundos (valor decimal)
  - **Tipo de superficie**: `stable`, `bosu`, `slackline`, `foam_pad`, `unstable`
  - **Ojos cerrados**: Booleano (`true`/`false`)
  - **Caídas o pérdidas de equilibrio**: Número entero
  - **Nivel de dificultad**: `1-10` escala
  - **Asimetría izquierda-derecha**: `symmetric`, `slight`, `marked`

### 8. **Coordinación (Boxing/Deportes de Raqueta)**
Mejora de la coordinación motora y tiempo de reacción.
- **Propiedades específicas:**
  - **Duración del ejercicio**: Segundos (entero)
  - **Porcentaje de precisión**: `0-100%` (valor decimal)
  - **Tiempo de reacción**: Milisegundos (valor decimal)
  - **Tiempo de respuesta**: Milisegundos (valor decimal)
  - **Porcentaje de secuencias correctas**: `0-100%` (valor decimal)
  - **Errores por minuto**: Valor decimal
  - **Velocidad de movimiento**: `slow`, `moderate`, `fast`, `very_fast`
  - **Calificación de sincronización**: `excellent`, `good`, `regular`, `poor`
  - **Nivel de complejidad**: `basic`, `intermediate`, `advanced`, `expert`
  - **Porcentaje de consistencia**: `0-100%` (valor decimal)

### 9. **Estabilidad Central (Core/Pilates)**
Fortalecimiento del núcleo y estabilidad postural.
- **Propiedades específicas:**
  - **Número de serie**: Número entero
  - **Tiempo de mantenimiento isométrico**: Segundos (entero)
  - **Repeticiones controladas**: Número entero
  - **Porcentaje de rango de movimiento**: `0-100%` (valor decimal)
  - **Calificación de estabilidad**: `excellent`, `good`, `regular`, `poor`
  - **Sensación de activación muscular**: `0-10` escala
  - **Nivel de dificultad**: `0-10` escala
  - **Nivel de fatiga local**: `none`, `light`, `moderate`, `high`, `extreme`
  - **Compensaciones posturales**: `none`, `light`, `moderate`, `severe`
  - **Coordinación respiratoria**: `synchronized`, `partial`, `unsynchronized`

## 🛠️ Tecnologías Utilizadas

- **Backend**: FastAPI (Python)
- **Base de Datos**: PostgreSQL con SQLAlchemy ORM
- **IA**: LangGraph + OpenAI GPT
- **Autenticación**: JWT con protección CSRF
- **Cache**: Sistema LRU personalizado
- **Contenarización**: Docker y Docker Compose

## 📊 Arquitectura

La aplicación sigue una arquitectura en capas modular:

```
📁 app/
├── 🤖 agent/              # Agente LLM y herramientas
│   ├── agent.py           # Lógica principal del agente
│   ├── tools/             # Herramientas específicas por disciplina
│   └── prompts.py         # Prompts del sistema
├── 🌐 api/                # API REST
│   ├── routes/            # Endpoints por dominio
│   └── services/          # Servicios de la API
├── ⚙️ core/               # Lógica de negocio principal
│   └── services/          # Servicios centrales
├── 🗄️ db/                 # Capa de acceso a datos
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Esquemas Pydantic
│   └── crud/              # Operaciones CRUD
├── 🔧 config/             # Configuración centralizada
├── 🛡️ middleware/         # Middleware de seguridad
└── 📋 utils/              # Utilidades generales
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.9+
- PostgreSQL 12+
- Docker (opcional)

### Configuración Rápida

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd fitcoachai/apps/backend
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. **Ejecutar con Docker**
```bash
docker-compose up -d
```

### Configuración de Desarrollo

Para configuración de desarrollo, ejecuta:
```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

## 🔑 Variables de Entorno Principales

```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost/fitcoachai

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Configuración de la aplicación
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000

# JWT y seguridad
SECRET_KEY=your-secret-key
```

## 📝 Uso de la API

### Autenticación
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

### Iniciar Entrenamiento
```bash
POST /api/workouts/start
{
  "workout_type": "strength_training"
}
```

### Registrar Ejercicio
```bash
POST /api/chat/message
{
  "message": "Completé 3 series de sentadillas con 100kg, 8 repeticiones cada una, RPE 8"
}
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app
```

## 📈 Características Avanzadas

- **Cache LRU Inteligente**: Optimiza el rendimiento del agente
- **Persistencia de Conversaciones**: Mantiene el contexto entre sesiones
- **Rate Limiting**: Protección contra abuso de la API
- **Logs Estructurados**: Monitoreo y debugging avanzado
- **Métricas de Rendimiento**: Análisis de progreso detallado

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte y preguntas:
- 📧 Email: support@fitcoachai.com
- 📖 Documentación: `/docs` (Swagger UI)
- 🐛 Issues: GitHub Issues

---

**FitCoach AI** - Transformando el fitness con inteligencia artificial 🚀

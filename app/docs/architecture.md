# FitCoach AI Architecture

This document describes the overall architecture of FitCoach AI, an AI-powered fitness coaching application.

## Project Structure

The application is structured following a modular and layer-oriented architectural pattern:

```
app/
├── agent/                # LLM Agent and its tools
├── api/                  # REST API
│   ├── routes/           # API Endpoints
│   └── services/         # API-specific services
├── config/               # Centralized configuration
├── core/                 # Main business logic
│   └── services/         # Core application services
├── db/                   # Data access layer
│   ├── crud/             # CRUD operations
│   ├── models/           # SQLAlchemy models
│   └── schemas/          # Pydantic schemas
├── exceptions/           # Custom exceptions
├── middleware/           # FastAPI middleware
├── tests/                # Unit and integration tests
└── utils/                # General utilities
```

## Application Layers

1. **Presentation Layer**

   * `api/routes/`: REST endpoints that handle HTTP requests and responses.
   * `middleware/`: Request processing before reaching the route layer.

2. **Business Layer**

   * `core/services/`: Implements the main business logic.
   * `agent/`: Integrates the language model and its specific logic.

3. **Data Layer**

   * `db/models/`: Defines the database structure.
   * `db/crud/`: Implements data access operations.

4. **Infrastructure Layer**

   * `config/`: Manages the application configuration.
   * `utils/`: Provides reusable functionalities.

## Data Flow

1. The HTTP request arrives at the application.
2. Middlewares process the request (rate limiting, security, etc.).
3. Routers direct the request to the appropriate controller.
4. Services implement the business logic.
5. CRUD models interact with the database.
6. The response is processed and returned to the client.

## Key Components

### LLM Agent

The main component is an LLM agent built with LangGraph that:

1. Receives user queries about fitness.
2. Uses tools like `log_exercise` to record exercises.
3. Provides personalized workout responses.

### Authentication and Security

* JWT for user authentication.
* CSRF protection to prevent attacks.
* Rate limiting to prevent abuse.
* Security headers for additional protection.

### Database

We use PostgreSQL with:

* SQLAlchemy as the ORM.
* Models to represent users, workouts, and exercise logs.
* Migrations with Alembic to manage schema changes.

## Design Patterns

* **Dependency Injection**: FastAPI allows dependency injection, such as for the DB session.
* **Repository**: The CRUD layer implements the repository pattern.
* **Services**: Logic is encapsulated in reusable services.
* **Middlewares**: Implement the decorator pattern to modify behavior.

## Scalability

The application is designed to scale horizontally:

* The database can scale independently.
* Stateless components can be replicated.
* Redis is used for distributed rate limiting.
* LangGraph enables persistence and retrieval of conversation states.

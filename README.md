# Inventario Recetas IA

Aplicación web que permite a los usuarios registrar ingredientes disponibles en casa y obtener recetas generadas por inteligencia artificial a partir de ese inventario.

## Descripción

El sistema integra un modelo de lenguaje (LLM) a través de OpenRouter para generar recetas estructuradas basadas en los ingredientes disponibles del usuario. Las recetas generadas se almacenan en base de datos y el usuario puede calificarlas, guardarlas o eliminarlas.

## Tecnologías utilizadas

- **Backend**: Python 3.11 + FastAPI
- **Base de datos**: PostgreSQL con SQLAlchemy ORM + Alembic (migraciones)
- **Autenticación**: JWT (JSON Web Tokens) con bcrypt
- **LLM**: OpenRouter API (modelos como Mistral, LLaMA, etc.)
- **Contenedores**: Docker + Docker Compose
- **Frontend**: HTML + Jinja2
- **Pruebas**: Pytest + pytest-asyncio

## Estructura del proyecto

```
Inventario_Recetas_IA/
├── app/
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── database.py          # Configuración de la conexión a PostgreSQL
│   ├── auth/
│   │   └── auth.py          # JWT, bcrypt, dependencia get_current_user
│   ├── models/
│   │   └── models.py        # Modelos ORM de las cuatro tablas
│   ├── routers/
│   │   ├── users.py         # Endpoints de autenticación
│   │   ├── ingredients.py   # CRUD de ingredientes
│   │   ├── recipes.py       # Generación y gestión de recetas
│   │   ├── ratings.py       # Calificación de recetas
│   │   └── frontend.py      # Vistas HTML
│   ├── services/
│   │   └── llm_service.py   # Integración con OpenRouter
│   └── schemas/
│       └── schemas.py       # Esquemas Pydantic de validación
├── tests/
│   ├── conftest.py               # Fixtures: BD de prueba, cliente, usuario
│   ├── test_auth.py              # Pruebas de hashing y JWT
│   ├── test_schemas.py           # Pruebas de validación Pydantic
│   ├── test_llm_service.py       # Pruebas de prompt y parseo LLM
│   ├── test_ingredients_api.py   # Pruebas de endpoints de ingredientes
│   └── test_recipes_api.py       # Pruebas de recetas y calificaciones
├── templates/
│   ├── base.html            # Plantilla base con navegación
│   └── index.html           # Página de inicio
├── alembic/
│   ├── env.py               # Configuración de migraciones
│   └── versions/
│       └── 0001_crear_tablas_iniciales.py
├── deploy/
│   ├── nginx.conf           # Configuración Nginx con SSL
│   └── setup_vps.sh         # Script de instalación en VPS
├── static/
│   └── favicon.ico
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── pytest.ini
├── .env.example
├── requirements.txt
└── README.md
```

## Requisitos previos

- Docker y Docker Compose instalados
- Clave de API de OpenRouter (https://openrouter.ai)

## Instalación y ejecución

### Con Docker (recomendado)

1. Clonar el repositorio:
```bash
git clone https://github.com/Airlin0108/Inventario_Recetas_IA.git
cd Inventario_Recetas_IA
```

2. Copiar el archivo de variables de entorno y configurarlo:
```bash
cp .env.example .env
# Editar .env con tus credenciales reales
```

3. Levantar los servicios:
```bash
docker compose up --build
```

4. Acceder a la aplicación:
   - Interfaz web: `http://localhost:8000`
   - Documentación API (Swagger): `http://localhost:8000/docs`

### Ejecución local (sin Docker)

```bash
pip install -r requirements.txt
cp .env.example .env   # Editar con tu PostgreSQL local
uvicorn app.main:app --reload
```

## Endpoints de la API

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/auth/register` | Registro de nuevo usuario | No |
| POST | `/auth/login` | Inicio de sesión → token JWT | No |
| GET | `/auth/me` | Perfil del usuario autenticado | Si |
| GET | `/ingredients/` | Listar ingredientes del inventario | Si |
| POST | `/ingredients/` | Agregar ingrediente | Si |
| PUT | `/ingredients/{id}` | Actualizar cantidad/unidad | Si |
| DELETE | `/ingredients/{id}` | Eliminar ingrediente | Si |
| POST | `/recipes/generate` | Generar receta con IA | Si |
| GET | `/recipes/` | Listar recetas guardadas | Si |
| GET | `/recipes/{id}` | Detalle de una receta | Si |
| DELETE | `/recipes/{id}` | Eliminar receta | Si |
| POST | `/recipes/{id}/rate` | Calificar receta (1-5) | Si |
| GET | `/recipes/{id}/ratings` | Listar calificaciones | Si |
| DELETE | `/recipes/{id}/rate` | Eliminar calificacion propia | Si |

## Pruebas unitarias

El proyecto incluye más de 40 pruebas organizadas en 5 archivos:

```bash
pytest tests/ -v
```

Cobertura de pruebas:
- **test_auth.py** — hashing bcrypt, creación/decodificación de tokens JWT
- **test_schemas.py** — validación de ingredientes, usuarios y calificaciones
- **test_llm_service.py** — construcción del prompt, parseo de JSON del LLM
- **test_ingredients_api.py** — registro, login y CRUD completo de ingredientes
- **test_recipes_api.py** — generación de recetas (LLM simulado), calificaciones

## Migraciones de base de datos

```bash
# Aplicar migraciones
alembic upgrade head

# Crear nueva migración
alembic revision --autogenerate -m "descripcion del cambio"
```

## Despliegue en VPS

Ver `deploy/nginx.conf` para la configuración de Nginx con SSL y `deploy/setup_vps.sh` para el script de instalación automática en Ubuntu 22.04.

```bash
# En el VPS, levantar con Docker Compose
docker compose up -d --build
```

## Variables de entorno

Consultar `.env.example` para ver todas las variables necesarias con sus descripciones.

## Equipo de desarrollo

- **Airlin Silvera** — Fase 1: estructura base, modelos, autenticación, ingredientes
- **Diego Martinez** — Fase 2: servicio LLM, recetas, calificaciones, Docker, frontend
- **Samuel Ortega** — Fase 3: pruebas unitarias, Alembic, despliegue, documentación

## Licencia

MIT

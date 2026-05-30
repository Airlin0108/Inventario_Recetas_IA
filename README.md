# Inventario_Recetas_IA

Aplicación web que permite a los usuarios registrar ingredientes disponibles en casa y obtener recetas generadas por inteligencia artificial a partir de ese inventario.

## Descripción

El sistema integra un modelo de lenguaje (LLM) a través de OpenRouter para generar recetas estructuradas basadas en los ingredientes disponibles del usuario. Las recetas generadas se almacenan en base de datos y el usuario puede calificarlas, guardarlas o eliminarlas.

## Tecnologías utilizadas

- **Backend**: Python 3.11 + FastAPI
- **Base de datos**: PostgreSQL con SQLAlchemy ORM
- **Autenticación**: JWT (JSON Web Tokens)
- **LLM**: OpenRouter API (modelos como Mistral, LLaMA, etc.)
- **Contenedores**: Docker + Docker Compose
- **Pruebas**: Pytest

## Estructura del proyecto

```
proyecto-recetas/
├── app/
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── database.py          # Configuración de la conexión a PostgreSQL
│   ├── models/
│   │   └── models.py        # Modelos ORM de las tablas
│   ├── routers/
│   │   ├── users.py         # Endpoints de autenticación
│   │   ├── ingredients.py   # Endpoints de gestión de ingredientes
│   │   └── recipes.py       # Endpoints de generación de recetas
│   ├── services/
│   │   └── llm_service.py   # Servicio de integración con LLM
│   └── schemas/
│       └── schemas.py       # Esquemas Pydantic de validación
├── tests/
│   └── test_*.py            # Pruebas unitarias
├── static/
│   └── favicon.ico
├── docker-compose.yml
├── Dockerfile
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
# Editar .env con tus credenciales
```

3. Levantar los servicios:
```bash
docker-compose up --build
```

4. Acceder a la aplicación en `http://localhost:8000`

5. Documentación automática de la API: `http://localhost:8000/docs`

### Ejecución local (sin Docker)

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno en archivo `.env`

3. Ejecutar la aplicación:
```bash
uvicorn app.main:app --reload
```

## Variables de entorno

Consultar `.env.example` para ver todas las variables necesarias con sus descripciones.

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/register` | Registro de nuevo usuario |
| POST | `/auth/login` | Inicio de sesión y obtención de token JWT |
| GET | `/ingredients/` | Listar ingredientes del usuario |
| POST | `/ingredients/` | Agregar ingrediente al inventario |
| DELETE | `/ingredients/{id}` | Eliminar ingrediente del inventario |
| POST | `/recipes/generate` | Generar receta basada en inventario actual |
| GET | `/recipes/` | Listar recetas guardadas del usuario |
| POST | `/recipes/{id}/rate` | Calificar una receta |
| DELETE | `/recipes/{id}` | Eliminar una receta guardada |

## Pruebas

```bash
pytest tests/ -v
```

## Despliegue

La aplicación está diseñada para desplegarse en un VPS con dominio propio y certificado SSL. Ver la sección de Docker para instrucciones de despliegue en producción.

## Equipo de desarrollo

- Airlin silvera
- Iver Masco

## Licencia

MIT

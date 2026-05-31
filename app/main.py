import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import create_tables
from app.routers import users, ingredients, recipes, ratings, frontend

app = FastAPI(
    title=os.getenv("APP_NAME", "Inventario Recetas IA"),
    description=(
        "API REST para gestionar un inventario de ingredientes y generar recetas "
        "mediante inteligencia artificial con LLM a traves de OpenRouter."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Orígenes permitidos para CORS. En producción se definen en la variable
# CORS_ORIGINS (separados por comas, ej: "https://midominio.com").
# Si queda vacía no se permite ningún origen cruzado: la interfaz web se sirve
# desde el mismo origen que la API, por lo que no necesita CORS para funcionar.
_cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(users.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(ratings.router)
app.include_router(frontend.router)


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/", response_class=HTMLResponse, tags=["Raiz"], include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", tags=["Raiz"])
def health_check():
    return {"status": "ok"}

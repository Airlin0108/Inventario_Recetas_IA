import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(users.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)
app.include_router(ratings.router)
app.include_router(frontend.router)


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/", tags=["Raiz"])
def root():
    return {
        "mensaje": "Bienvenido a Inventario Recetas IA",
        "documentacion": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Raiz"])
def health_check():
    return {"status": "ok"}

import os
import json
import httpx
from typing import List
from dotenv import load_dotenv
from app.schemas.schemas import RecetaGenerada

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")


def _construir_prompt(ingredientes: List[dict]) -> str:
    lista = "\n".join(
        f"- {ing['nombre']}: {ing['cantidad']} {ing['unidad']}"
        for ing in ingredientes
    )
    return f"""Eres un chef experto. El usuario tiene los siguientes ingredientes disponibles:

{lista}

Genera UNA receta detallada usando solo (o la mayoría de) esos ingredientes.
Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta, sin texto adicional:

{{
  "nombre_plato": "string",
  "ingredientes": [
    {{"nombre": "string", "cantidad": "string", "unidad": "string"}}
  ],
  "pasos_preparacion": ["string", "string"],
  "tiempo_estimado": "string (ej: 30 minutos)",
  "nivel_dificultad": "Fácil | Medio | Difícil"
}}"""


def _parsear_respuesta(contenido: str) -> RecetaGenerada:
    contenido = contenido.strip()
    if contenido.startswith("```"):
        lineas = contenido.split("\n")
        contenido = "\n".join(lineas[1:-1])
    datos = json.loads(contenido)
    return RecetaGenerada(**datos)


async def generar_receta(ingredientes: List[dict]) -> RecetaGenerada:
    if not OPENROUTER_API_KEY:
        raise ValueError("La variable OPENROUTER_API_KEY no está configurada en el entorno")

    prompt = _construir_prompt(ingredientes)

    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1200,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://inventario-recetas.app",
        "X-Title": "Inventario Recetas IA",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()

    resultado = response.json()
    contenido = resultado["choices"][0]["message"]["content"]
    return _parsear_respuesta(contenido)

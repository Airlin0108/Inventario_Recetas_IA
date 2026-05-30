import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.llm_service import _construir_prompt, _parsear_respuesta, generar_receta
from app.schemas.schemas import RecetaGenerada


INGREDIENTES_EJEMPLO = [
    {"nombre": "Pollo", "cantidad": 500, "unidad": "gramos"},
    {"nombre": "Arroz", "cantidad": 200, "unidad": "gramos"},
    {"nombre": "Cebolla", "cantidad": 1, "unidad": "unidad"},
]

RESPUESTA_LLM_VALIDA = json.dumps({
    "nombre_plato": "Arroz con Pollo",
    "ingredientes": [
        {"nombre": "Pollo", "cantidad": "500", "unidad": "gramos"},
        {"nombre": "Arroz", "cantidad": "200", "unidad": "gramos"},
    ],
    "pasos_preparacion": [
        "Cortar el pollo en trozos medianos.",
        "Sofreir la cebolla hasta que este dorada.",
        "Agregar el arroz y el pollo, cubrir con agua y cocinar 20 minutos.",
    ],
    "tiempo_estimado": "35 minutos",
    "nivel_dificultad": "Fácil",
})


class TestConstruccionDelPrompt:
    def test_prompt_contiene_nombres_de_ingredientes(self):
        prompt = _construir_prompt(INGREDIENTES_EJEMPLO)
        assert "Pollo" in prompt
        assert "Arroz" in prompt
        assert "Cebolla" in prompt

    def test_prompt_contiene_cantidades_y_unidades(self):
        prompt = _construir_prompt(INGREDIENTES_EJEMPLO)
        assert "500" in prompt
        assert "gramos" in prompt

    def test_prompt_pide_respuesta_en_formato_json(self):
        prompt = _construir_prompt(INGREDIENTES_EJEMPLO)
        assert "JSON" in prompt or "json" in prompt

    def test_prompt_incluye_todos_los_campos_requeridos(self):
        prompt = _construir_prompt(INGREDIENTES_EJEMPLO)
        campos = ["nombre_plato", "ingredientes", "pasos_preparacion", "tiempo_estimado", "nivel_dificultad"]
        for campo in campos:
            assert campo in prompt

    def test_prompt_con_lista_vacia_no_falla(self):
        prompt = _construir_prompt([])
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestParseoRespuestaLLM:
    def test_parsea_json_valido_en_schema_receta_generada(self):
        receta = _parsear_respuesta(RESPUESTA_LLM_VALIDA)
        assert isinstance(receta, RecetaGenerada)
        assert receta.nombre_plato == "Arroz con Pollo"

    def test_pasos_son_lista_de_strings(self):
        receta = _parsear_respuesta(RESPUESTA_LLM_VALIDA)
        assert isinstance(receta.pasos_preparacion, list)
        assert len(receta.pasos_preparacion) == 3

    def test_ingredientes_son_lista_de_dicts(self):
        receta = _parsear_respuesta(RESPUESTA_LLM_VALIDA)
        assert isinstance(receta.ingredientes, list)
        assert all(isinstance(i, dict) for i in receta.ingredientes)

    def test_parsea_respuesta_con_bloque_markdown(self):
        envuelta = f"```json\n{RESPUESTA_LLM_VALIDA}\n```"
        receta = _parsear_respuesta(envuelta)
        assert receta.nombre_plato == "Arroz con Pollo"

    def test_parseo_de_json_invalido_lanza_excepcion(self):
        with pytest.raises(Exception):
            _parsear_respuesta("esto no es json valido {{{")


class TestGenerarRecetaIntegracion:
    @pytest.mark.asyncio
    async def test_genera_receta_con_api_simulada(self):
        respuesta_mock = MagicMock()
        respuesta_mock.json.return_value = {
            "choices": [{"message": {"content": RESPUESTA_LLM_VALIDA}}]
        }
        respuesta_mock.raise_for_status = MagicMock()

        with patch("app.services.llm_service.OPENROUTER_API_KEY", "sk-test-key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__ = AsyncMock(return_value=MagicMock(
                    post=AsyncMock(return_value=respuesta_mock)
                ))
                mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
                receta = await generar_receta(INGREDIENTES_EJEMPLO)

        assert receta.nombre_plato == "Arroz con Pollo"
        assert receta.nivel_dificultad == "Fácil"

    @pytest.mark.asyncio
    async def test_lanza_error_si_falta_api_key(self):
        with patch("app.services.llm_service.OPENROUTER_API_KEY", ""):
            with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
                await generar_receta(INGREDIENTES_EJEMPLO)

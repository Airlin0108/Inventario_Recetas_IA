import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.schemas.schemas import RecetaGenerada


RECETA_MOCK = RecetaGenerada(
    nombre_plato="Sopa de Verduras",
    ingredientes=[{"nombre": "Zanahoria", "cantidad": "2", "unidad": "unidades"}],
    pasos_preparacion=["Pelar las zanahorias.", "Hervir 20 minutos.", "Servir caliente."],
    tiempo_estimado="25 minutos",
    nivel_dificultad="Fácil",
)


def _agregar_ingrediente(client, headers, nombre="Zanahoria", cantidad=2, unidad="unidades"):
    return client.post("/ingredients/", json={
        "nombre": nombre, "cantidad": cantidad, "unidad": unidad
    }, headers=headers)


class TestGeneracionDeRecetas:
    def test_generar_sin_ingredientes_devuelve_400(self, client, headers_auth):
        resp = client.post("/recipes/generate", headers=headers_auth)
        assert resp.status_code == 400

    def test_generar_receta_con_llm_simulado_devuelve_201(self, client, headers_auth):
        _agregar_ingrediente(client, headers_auth, "Papas")
        with patch("app.routers.recipes.generar_receta", new=AsyncMock(return_value=RECETA_MOCK)):
            resp = client.post("/recipes/generate", headers=headers_auth)
        assert resp.status_code == 201
        assert resp.json()["nombre_plato"] == "Sopa de Verduras"

    def test_receta_generada_contiene_campos_obligatorios(self, client, headers_auth):
        _agregar_ingrediente(client, headers_auth, "Tomate")
        with patch("app.routers.recipes.generar_receta", new=AsyncMock(return_value=RECETA_MOCK)):
            resp = client.post("/recipes/generate", headers=headers_auth)
        datos = resp.json()
        for campo in ["id", "nombre_plato", "ingredientes", "pasos_preparacion", "tiempo_estimado", "nivel_dificultad"]:
            assert campo in datos

    def test_generar_receta_sin_token_devuelve_401(self, client):
        resp = client.post("/recipes/generate")
        assert resp.status_code == 401


class TestConsultaDeRecetas:
    def _crear_receta(self, client, headers_auth):
        _agregar_ingrediente(client, headers_auth, "Lechuga")
        with patch("app.routers.recipes.generar_receta", new=AsyncMock(return_value=RECETA_MOCK)):
            return client.post("/recipes/generate", headers=headers_auth)

    def test_listar_recetas_devuelve_lista(self, client, headers_auth):
        resp = client.get("/recipes/", headers=headers_auth)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_obtener_receta_por_id_valido(self, client, headers_auth):
        creada = self._crear_receta(client, headers_auth)
        receta_id = creada.json()["id"]
        resp = client.get(f"/recipes/{receta_id}", headers=headers_auth)
        assert resp.status_code == 200
        assert resp.json()["id"] == receta_id

    def test_obtener_receta_inexistente_devuelve_404(self, client, headers_auth):
        resp = client.get("/recipes/99999", headers=headers_auth)
        assert resp.status_code == 404

    def test_eliminar_receta_existente_devuelve_204(self, client, headers_auth):
        creada = self._crear_receta(client, headers_auth)
        receta_id = creada.json()["id"]
        resp = client.delete(f"/recipes/{receta_id}", headers=headers_auth)
        assert resp.status_code == 204


class TestCalificacionDeRecetas:
    def _crear_receta(self, client, headers_auth):
        _agregar_ingrediente(client, headers_auth, "Espinaca")
        with patch("app.routers.recipes.generar_receta", new=AsyncMock(return_value=RECETA_MOCK)):
            return client.post("/recipes/generate", headers=headers_auth)

    def test_calificar_receta_con_puntuacion_valida(self, client, headers_auth):
        creada = self._crear_receta(client, headers_auth)
        receta_id = creada.json()["id"]
        resp = client.post(f"/recipes/{receta_id}/rate", json={
            "puntuacion": 5, "comentario": "Excelente receta"
        }, headers=headers_auth)
        assert resp.status_code == 201
        assert resp.json()["puntuacion"] == 5

    def test_calificacion_promedio_se_refleja_en_detalle_de_receta(self, client, headers_auth):
        creada = self._crear_receta(client, headers_auth)
        receta_id = creada.json()["id"]
        client.post(f"/recipes/{receta_id}/rate", json={"puntuacion": 4}, headers=headers_auth)
        resp = client.get(f"/recipes/{receta_id}", headers=headers_auth)
        assert resp.json()["calificacion_promedio"] == 4.0

    def test_calificar_con_puntuacion_fuera_de_rango_devuelve_422(self, client, headers_auth):
        creada = self._crear_receta(client, headers_auth)
        receta_id = creada.json()["id"]
        resp = client.post(f"/recipes/{receta_id}/rate", json={"puntuacion": 10}, headers=headers_auth)
        assert resp.status_code == 422

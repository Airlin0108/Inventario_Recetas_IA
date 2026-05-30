import pytest


class TestRegistroDeUsuario:
    def test_registro_exitoso_devuelve_201(self, client):
        resp = client.post("/auth/register", json={
            "nombre": "Nuevo Usuario",
            "email": "nuevo@test.com",
            "password": "Valida123",
        })
        assert resp.status_code == 201
        assert resp.json()["email"] == "nuevo@test.com"

    def test_registro_con_email_duplicado_devuelve_400(self, client):
        datos = {"nombre": "Dup", "email": "dup@test.com", "password": "Valida123"}
        client.post("/auth/register", json=datos)
        resp = client.post("/auth/register", json=datos)
        assert resp.status_code == 400

    def test_login_con_credenciales_correctas_devuelve_token(self, client):
        client.post("/auth/register", json={
            "nombre": "Login User",
            "email": "login@test.com",
            "password": "Login123",
        })
        resp = client.post("/auth/login", json={
            "email": "login@test.com",
            "password": "Login123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_con_contrasena_incorrecta_devuelve_401(self, client):
        client.post("/auth/register", json={
            "nombre": "Test401",
            "email": "test401@test.com",
            "password": "Correcta123",
        })
        resp = client.post("/auth/login", json={
            "email": "test401@test.com",
            "password": "Incorrecta999",
        })
        assert resp.status_code == 401


class TestGestionDeIngredientes:
    def test_listar_ingredientes_sin_auth_devuelve_401(self, client):
        resp = client.get("/ingredients/")
        assert resp.status_code == 401

    def test_listar_ingredientes_con_auth_devuelve_lista_vacia(self, client, headers_auth):
        resp = client.get("/ingredients/", headers=headers_auth)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_agregar_ingrediente_valido_devuelve_201(self, client, headers_auth):
        resp = client.post("/ingredients/", json={
            "nombre": "Zanahoria",
            "cantidad": 3,
            "unidad": "unidades",
        }, headers=headers_auth)
        assert resp.status_code == 201
        assert resp.json()["nombre"] == "Zanahoria"

    def test_agregar_ingrediente_duplicado_devuelve_400(self, client, headers_auth):
        datos = {"nombre": "Pepino", "cantidad": 2, "unidad": "unidades"}
        client.post("/ingredients/", json=datos, headers=headers_auth)
        resp = client.post("/ingredients/", json=datos, headers=headers_auth)
        assert resp.status_code == 400

    def test_agregar_ingrediente_con_cantidad_cero_devuelve_422(self, client, headers_auth):
        resp = client.post("/ingredients/", json={
            "nombre": "Aceite",
            "cantidad": 0,
            "unidad": "ml",
        }, headers=headers_auth)
        assert resp.status_code == 422

    def test_eliminar_ingrediente_inexistente_devuelve_404(self, client, headers_auth):
        resp = client.delete("/ingredients/99999", headers=headers_auth)
        assert resp.status_code == 404

    def test_actualizar_cantidad_de_ingrediente(self, client, headers_auth):
        crear = client.post("/ingredients/", json={
            "nombre": "Mantequilla",
            "cantidad": 100,
            "unidad": "gramos",
        }, headers=headers_auth)
        ing_id = crear.json()["id"]
        resp = client.put(f"/ingredients/{ing_id}", json={"cantidad": 250}, headers=headers_auth)
        assert resp.status_code == 200
        assert resp.json()["cantidad"] == 250

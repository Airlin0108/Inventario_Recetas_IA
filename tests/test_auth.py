import pytest
from jose import jwt
from app.auth.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    SECRET_KEY,
    ALGORITHM,
)


class TestHasheoContrasena:
    def test_hash_genera_cadena_diferente_al_texto_plano(self):
        hashed = hash_password("MiContrasena123")
        assert hashed != "MiContrasena123"

    def test_hash_produce_formato_bcrypt(self):
        hashed = hash_password("MiContrasena123")
        assert hashed.startswith("$2b$")

    def test_verificacion_correcta_devuelve_true(self):
        hashed = hash_password("Secreta456")
        assert verify_password("Secreta456", hashed) is True

    def test_verificacion_con_contrasena_incorrecta_devuelve_false(self):
        hashed = hash_password("Correcta789")
        assert verify_password("Incorrecta000", hashed) is False

    def test_dos_hashes_del_mismo_texto_son_distintos(self):
        h1 = hash_password("Misma1")
        h2 = hash_password("Misma1")
        assert h1 != h2


class TestTokenJWT:
    def test_token_creado_es_decodificable(self):
        token = create_access_token(data={"sub": "42"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "42"

    def test_token_contiene_campo_exp(self):
        token = create_access_token(data={"sub": "1"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_decode_token_retorna_payload_correcto(self):
        token = create_access_token(data={"sub": "99", "rol": "admin"})
        payload = decode_token(token)
        assert payload["sub"] == "99"

    def test_decode_token_invalido_lanza_http_401(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_token("token.completamente.invalido")
        assert exc_info.value.status_code == 401

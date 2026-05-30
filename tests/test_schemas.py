import pytest
from pydantic import ValidationError
from app.schemas.schemas import (
    IngredienteCreate,
    IngredienteUpdate,
    UsuarioCreate,
    CalificacionCreate,
)


class TestValidacionIngrediente:
    def test_ingrediente_valido_se_crea_correctamente(self):
        ing = IngredienteCreate(nombre="Tomate", cantidad=3.0, unidad="unidades")
        assert ing.nombre == "Tomate"
        assert ing.cantidad == 3.0

    def test_nombre_demasiado_corto_lanza_error(self):
        with pytest.raises(ValidationError):
            IngredienteCreate(nombre="T", cantidad=1.0, unidad="kg")

    def test_cantidad_cero_lanza_error(self):
        with pytest.raises(ValidationError):
            IngredienteCreate(nombre="Arroz", cantidad=0, unidad="kg")

    def test_cantidad_negativa_lanza_error(self):
        with pytest.raises(ValidationError):
            IngredienteCreate(nombre="Leche", cantidad=-1.5, unidad="litros")

    def test_unidad_vacia_lanza_error(self):
        with pytest.raises(ValidationError):
            IngredienteCreate(nombre="Sal", cantidad=0.5, unidad="")

    def test_ingrediente_update_permite_campos_opcionales(self):
        update = IngredienteUpdate(cantidad=2.5)
        assert update.cantidad == 2.5
        assert update.nombre is None
        assert update.unidad is None


class TestValidacionUsuario:
    def test_usuario_valido_con_contrasena_con_numero(self):
        user = UsuarioCreate(nombre="Ana Lopez", email="ana@test.com", password="Segura123")
        assert user.email == "ana@test.com"

    def test_contrasena_sin_numero_lanza_error(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nombre="Juan", email="juan@test.com", password="sololetras")

    def test_contrasena_demasiado_corta_lanza_error(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nombre="Maria", email="maria@test.com", password="Ab1")

    def test_email_invalido_lanza_error(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nombre="Pedro", email="no-es-email", password="Valida123")


class TestValidacionCalificacion:
    def test_puntuacion_valida_entre_1_y_5(self):
        cal = CalificacionCreate(puntuacion=4, comentario="Muy buena receta")
        assert cal.puntuacion == 4

    def test_puntuacion_cero_lanza_error(self):
        with pytest.raises(ValidationError):
            CalificacionCreate(puntuacion=0)

    def test_puntuacion_mayor_a_5_lanza_error(self):
        with pytest.raises(ValidationError):
            CalificacionCreate(puntuacion=6)

    def test_comentario_es_opcional(self):
        cal = CalificacionCreate(puntuacion=3)
        assert cal.comentario is None

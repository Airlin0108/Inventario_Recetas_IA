from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


# ─── Esquemas de Usuario ──────────────────────────────────────────────────────

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un numero")
        return v


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    activo: bool
    fecha_registro: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


# ─── Esquemas de Ingrediente ──────────────────────────────────────────────────

class IngredienteCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    cantidad: float = Field(..., gt=0)
    unidad: str = Field(..., min_length=1, max_length=30)


class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    cantidad: Optional[float] = Field(None, gt=0)
    unidad: Optional[str] = Field(None, min_length=1, max_length=30)


class IngredienteResponse(BaseModel):
    id: int
    nombre: str
    cantidad: float
    unidad: str
    fecha_agregado: datetime
    usuario_id: int

    model_config = {"from_attributes": True}


# ─── Esquemas de Receta ───────────────────────────────────────────────────────

class RecetaResponse(BaseModel):
    id: int
    nombre_plato: str
    ingredientes_json: str
    pasos_preparacion: str
    tiempo_estimado: str
    nivel_dificultad: str
    fecha_generacion: datetime
    guardada: bool
    usuario_id: int

    model_config = {"from_attributes": True}


class RecetaDetalleResponse(BaseModel):
    id: int
    nombre_plato: str
    ingredientes: List[dict]
    pasos_preparacion: List[str]
    tiempo_estimado: str
    nivel_dificultad: str
    fecha_generacion: datetime
    guardada: bool
    calificacion_promedio: Optional[float] = None
    total_calificaciones: int = 0

    model_config = {"from_attributes": False}


class RecetaGenerada(BaseModel):
    nombre_plato: str
    ingredientes: List[dict]
    pasos_preparacion: List[str]
    tiempo_estimado: str
    nivel_dificultad: str


# ─── Esquemas de Calificacion ─────────────────────────────────────────────────

class CalificacionCreate(BaseModel):
    puntuacion: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = Field(None, max_length=500)


class CalificacionResponse(BaseModel):
    id: int
    puntuacion: int
    comentario: Optional[str]
    fecha_calificacion: datetime
    receta_id: int
    usuario_id: int

    model_config = {"from_attributes": True}

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Ingrediente, Usuario
from app.schemas.schemas import IngredienteCreate, IngredienteUpdate, IngredienteResponse
from app.auth.auth import get_current_user

router = APIRouter(prefix="/ingredients", tags=["Ingredientes"])


@router.get("/", response_model=List[IngredienteResponse])
def listar_ingredientes(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Devuelve todos los ingredientes del inventario del usuario autenticado."""
    return db.query(Ingrediente).filter(Ingrediente.usuario_id == usuario_actual.id).all()


@router.post("/", response_model=IngredienteResponse, status_code=status.HTTP_201_CREATED)
def agregar_ingrediente(
    datos: IngredienteCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Agrega un nuevo ingrediente al inventario del usuario."""
    duplicado = (
        db.query(Ingrediente)
        .filter(
            Ingrediente.usuario_id == usuario_actual.id,
            Ingrediente.nombre.ilike(datos.nombre),
        )
        .first()
    )
    if duplicado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El ingrediente '{datos.nombre}' ya existe en tu inventario",
        )
    nuevo = Ingrediente(**datos.model_dump(), usuario_id=usuario_actual.id)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{ingrediente_id}", response_model=IngredienteResponse)
def actualizar_ingrediente(
    ingrediente_id: int,
    datos: IngredienteUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Actualiza la cantidad o unidad de un ingrediente del inventario."""
    ingrediente = (
        db.query(Ingrediente)
        .filter(Ingrediente.id == ingrediente_id, Ingrediente.usuario_id == usuario_actual.id)
        .first()
    )
    if not ingrediente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingrediente no encontrado")

    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(ingrediente, campo, valor)
    db.commit()
    db.refresh(ingrediente)
    return ingrediente


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ingrediente(
    ingrediente_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Elimina un ingrediente del inventario del usuario."""
    ingrediente = (
        db.query(Ingrediente)
        .filter(Ingrediente.id == ingrediente_id, Ingrediente.usuario_id == usuario_actual.id)
        .first()
    )
    if not ingrediente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingrediente no encontrado")
    db.delete(ingrediente)
    db.commit()

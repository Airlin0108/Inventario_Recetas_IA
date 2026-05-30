import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Receta, Ingrediente, Usuario
from app.schemas.schemas import RecetaResponse, RecetaDetalleResponse
from app.auth.auth import get_current_user
from app.services.llm_service import generar_receta

router = APIRouter(prefix="/recipes", tags=["Recetas"])


def _receta_a_detalle(receta: Receta) -> RecetaDetalleResponse:
    calificaciones = receta.calificaciones
    promedio = (
        round(sum(c.puntuacion for c in calificaciones) / len(calificaciones), 2)
        if calificaciones
        else None
    )
    return RecetaDetalleResponse(
        id=receta.id,
        nombre_plato=receta.nombre_plato,
        ingredientes=json.loads(receta.ingredientes_json),
        pasos_preparacion=json.loads(receta.pasos_preparacion),
        tiempo_estimado=receta.tiempo_estimado,
        nivel_dificultad=receta.nivel_dificultad,
        fecha_generacion=receta.fecha_generacion,
        guardada=receta.guardada,
        calificacion_promedio=promedio,
        total_calificaciones=len(calificaciones),
    )


@router.post("/generate", response_model=RecetaDetalleResponse, status_code=status.HTTP_201_CREATED)
async def generar_receta_endpoint(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Genera una receta con IA usando el inventario actual del usuario y la guarda en base de datos."""
    ingredientes_db = (
        db.query(Ingrediente).filter(Ingrediente.usuario_id == usuario_actual.id).all()
    )
    if not ingredientes_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes agregar al menos un ingrediente a tu inventario antes de generar una receta",
        )

    ingredientes_lista = [
        {"nombre": ing.nombre, "cantidad": ing.cantidad, "unidad": ing.unidad}
        for ing in ingredientes_db
    ]

    try:
        receta_generada = await generar_receta(ingredientes_lista)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al comunicarse con el servicio de IA: {str(e)}",
        )

    nueva_receta = Receta(
        nombre_plato=receta_generada.nombre_plato,
        ingredientes_json=json.dumps(receta_generada.ingredientes, ensure_ascii=False),
        pasos_preparacion=json.dumps(receta_generada.pasos_preparacion, ensure_ascii=False),
        tiempo_estimado=receta_generada.tiempo_estimado,
        nivel_dificultad=receta_generada.nivel_dificultad,
        usuario_id=usuario_actual.id,
    )
    db.add(nueva_receta)
    db.commit()
    db.refresh(nueva_receta)
    return _receta_a_detalle(nueva_receta)


@router.get("/", response_model=List[RecetaDetalleResponse])
def listar_recetas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Devuelve todas las recetas guardadas del usuario autenticado con su calificacion promedio."""
    recetas = (
        db.query(Receta)
        .filter(Receta.usuario_id == usuario_actual.id, Receta.guardada == True)
        .order_by(Receta.fecha_generacion.desc())
        .all()
    )
    return [_receta_a_detalle(r) for r in recetas]


@router.get("/{receta_id}", response_model=RecetaDetalleResponse)
def obtener_receta(
    receta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Devuelve el detalle completo de una receta especifica del usuario."""
    receta = (
        db.query(Receta)
        .filter(Receta.id == receta_id, Receta.usuario_id == usuario_actual.id)
        .first()
    )
    if not receta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
    return _receta_a_detalle(receta)


@router.delete("/{receta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_receta(
    receta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Elimina permanentemente una receta guardada del usuario."""
    receta = (
        db.query(Receta)
        .filter(Receta.id == receta_id, Receta.usuario_id == usuario_actual.id)
        .first()
    )
    if not receta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
    db.delete(receta)
    db.commit()

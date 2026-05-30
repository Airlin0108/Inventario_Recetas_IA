from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Calificacion, Receta, Usuario
from app.schemas.schemas import CalificacionCreate, CalificacionResponse
from app.auth.auth import get_current_user

router = APIRouter(prefix="/recipes", tags=["Calificaciones"])


@router.post("/{receta_id}/rate", response_model=CalificacionResponse, status_code=status.HTTP_201_CREATED)
def calificar_receta(
    receta_id: int,
    datos: CalificacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Registra una calificacion del 1 al 5 para una receta guardada del usuario."""
    receta = (
        db.query(Receta)
        .filter(Receta.id == receta_id, Receta.usuario_id == usuario_actual.id)
        .first()
    )
    if not receta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada o no pertenece al usuario",
        )

    calificacion_previa = (
        db.query(Calificacion)
        .filter(
            Calificacion.receta_id == receta_id,
            Calificacion.usuario_id == usuario_actual.id,
        )
        .first()
    )
    if calificacion_previa:
        calificacion_previa.puntuacion = datos.puntuacion
        calificacion_previa.comentario = datos.comentario
        db.commit()
        db.refresh(calificacion_previa)
        return calificacion_previa

    nueva_calificacion = Calificacion(
        puntuacion=datos.puntuacion,
        comentario=datos.comentario,
        receta_id=receta_id,
        usuario_id=usuario_actual.id,
    )
    db.add(nueva_calificacion)
    db.commit()
    db.refresh(nueva_calificacion)
    return nueva_calificacion


@router.get("/{receta_id}/ratings", response_model=List[CalificacionResponse])
def listar_calificaciones(
    receta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Devuelve todas las calificaciones registradas para una receta especifica."""
    receta = db.query(Receta).filter(Receta.id == receta_id).first()
    if not receta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
    return (
        db.query(Calificacion)
        .filter(Calificacion.receta_id == receta_id)
        .order_by(Calificacion.fecha_calificacion.desc())
        .all()
    )


@router.delete("/{receta_id}/rate", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_calificacion(
    receta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    """Elimina la calificacion que el usuario dio a una receta."""
    calificacion = (
        db.query(Calificacion)
        .filter(
            Calificacion.receta_id == receta_id,
            Calificacion.usuario_id == usuario_actual.id,
        )
        .first()
    )
    if not calificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No has calificado esta receta",
        )
    db.delete(calificacion)
    db.commit()

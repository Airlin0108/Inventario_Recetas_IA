from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean,
    DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    ingredientes = relationship("Ingrediente", back_populates="usuario", cascade="all, delete-orphan")
    recetas = relationship("Receta", back_populates="usuario", cascade="all, delete-orphan")


class Ingrediente(Base):
    __tablename__ = "ingredientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    cantidad = Column(Float, nullable=False)
    unidad = Column(String(30), nullable=False)
    fecha_agregado = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="ingredientes")


class Receta(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre_plato = Column(String(200), nullable=False)
    ingredientes_json = Column(Text, nullable=False)
    pasos_preparacion = Column(Text, nullable=False)
    tiempo_estimado = Column(String(50), nullable=False)
    nivel_dificultad = Column(String(30), nullable=False)
    fecha_generacion = Column(DateTime, default=datetime.utcnow)
    guardada = Column(Boolean, default=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="recetas")
    calificaciones = relationship("Calificacion", back_populates="receta", cascade="all, delete-orphan")


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id = Column(Integer, primary_key=True, index=True)
    puntuacion = Column(Integer, nullable=False)
    comentario = Column(Text, nullable=True)
    fecha_calificacion = Column(DateTime, default=datetime.utcnow)
    receta_id = Column(Integer, ForeignKey("recetas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("puntuacion >= 1 AND puntuacion <= 5", name="check_puntuacion_rango"),
    )

    receta = relationship("Receta", back_populates="calificaciones")

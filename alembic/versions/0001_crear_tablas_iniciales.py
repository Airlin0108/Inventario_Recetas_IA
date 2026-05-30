"""Crear tablas iniciales: usuarios, ingredientes, recetas y calificaciones

Revision ID: 0001
Revises:
Create Date: 2025-05-30 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("email", sa.String(150), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default="true"),
        sa.Column("fecha_registro", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "ingredientes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("cantidad", sa.Float(), nullable=False),
        sa.Column("unidad", sa.String(30), nullable=False),
        sa.Column("fecha_agregado", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
    )

    op.create_table(
        "recetas",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nombre_plato", sa.String(200), nullable=False),
        sa.Column("ingredientes_json", sa.Text(), nullable=False),
        sa.Column("pasos_preparacion", sa.Text(), nullable=False),
        sa.Column("tiempo_estimado", sa.String(50), nullable=False),
        sa.Column("nivel_dificultad", sa.String(30), nullable=False),
        sa.Column("fecha_generacion", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("guardada", sa.Boolean(), server_default="true"),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
    )

    op.create_table(
        "calificaciones",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("puntuacion", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("fecha_calificacion", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("receta_id", sa.Integer(), sa.ForeignKey("recetas.id"), nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.CheckConstraint("puntuacion >= 1 AND puntuacion <= 5", name="check_puntuacion_rango"),
    )


def downgrade() -> None:
    op.drop_table("calificaciones")
    op.drop_table("recetas")
    op.drop_table("ingredientes")
    op.drop_table("usuarios")

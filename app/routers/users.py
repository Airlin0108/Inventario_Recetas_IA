from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Usuario
from app.schemas.schemas import UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse
from app.auth.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticacion"])


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario en el sistema."""
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cuenta registrada con ese correo electronico",
        )
    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        hashed_password=hash_password(datos.password),
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=TokenResponse)
def iniciar_sesion(credenciales: LoginRequest, db: Session = Depends(get_db)):
    """Autentica al usuario y devuelve un token JWT de acceso."""
    usuario = db.query(Usuario).filter(Usuario.email == credenciales.email).first()
    if not usuario or not verify_password(credenciales.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electronico o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta de usuario esta desactivada",
        )
    token = create_access_token(data={"sub": str(usuario.id)})
    return TokenResponse(access_token=token, usuario=UsuarioResponse.model_validate(usuario))


@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil(usuario_actual: Usuario = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado actualmente."""
    return usuario_actual

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.celda import Celda
from app.schemas.celda import CeldaCreate, CeldaOut, CeldaUpdate
from app.services.celda_service import celda_service

router = APIRouter()


@router.get("/", response_model=list[CeldaOut], dependencies=[Depends(get_current_user)])
def listar_celdas(db: Session = Depends(get_db)):
    return celda_service.listar_celdas(db)


@router.get("/disponibles", response_model=list[CeldaOut], dependencies=[Depends(get_current_user)])
def listar_celdas_disponibles(id_tipo: int | None = None, db: Session = Depends(get_db)):
    return celda_service.listar_disponibles(db, id_tipo=id_tipo)


@router.post("/", response_model=CeldaOut, status_code=status.HTTP_201_CREATED)
async def crear_celda(
    payload: CeldaCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    ip = request.client.host if request.client else None
    return await celda_service.crear_celda(db, payload, current_user, ip)


@router.get("/{id_celda}", response_model=CeldaOut, dependencies=[Depends(get_current_user)])
def obtener_celda(id_celda: int, db: Session = Depends(get_db)):
    celda = db.get(Celda, id_celda)
    if not celda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Celda no encontrada",
        )
    return celda


@router.put("/{id_celda}", response_model=CeldaOut)
async def actualizar_celda(
    id_celda: int,
    payload: CeldaUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    ip = request.client.host if request.client else None
    return await celda_service.actualizar_celda(db, id_celda, payload, current_user, ip)


@router.delete("/{id_celda}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_celda(
    id_celda: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_admin),
):
    ip = request.client.host if request.client else None
    await celda_service.eliminar_celda(db, id_celda, usuario_actual, ip)
    return None
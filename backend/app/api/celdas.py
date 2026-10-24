from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.celda import Celda
from app.models.tipo import Tipo
from app.schemas.celda import CeldaCreate, CeldaOut, CeldaUpdate

router = APIRouter()


@router.get("/", response_model=list[CeldaOut])
def listar_celdas(db: Session = Depends(get_db)):
    return db.query(Celda).all()


@router.get("/disponibles", response_model=list[CeldaOut])
def listar_celdas_disponibles(id_tipo: int | None = None, db: Session = Depends(get_db)):
    consulta = db.query(Celda).filter(Celda.estado == "LIBRE")
    if id_tipo is not None:
        consulta = consulta.filter(Celda.idTipo == id_tipo)
    return consulta.all()


@router.get("/{id_celda}", response_model=CeldaOut)
def obtener_celda(id_celda: int, db: Session = Depends(get_db)):
    celda = db.get(Celda, id_celda)
    if not celda:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Celda no encontrada")
    return celda


@router.post("/", response_model=CeldaOut, status_code=status.HTTP_201_CREATED)
def crear_celda(payload: CeldaCreate, db: Session = Depends(get_db)):
    if not db.get(Tipo, payload.idTipo):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")
    existente = db.query(Celda).filter(Celda.codigo == payload.codigo).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de celda ya existe")
    celda = Celda(**payload.model_dump())
    db.add(celda)
    db.commit()
    db.refresh(celda)
    return celda


@router.put("/{id_celda}", response_model=CeldaOut)
def actualizar_celda(id_celda: int, payload: CeldaUpdate, db: Session = Depends(get_db)):
    celda = db.get(Celda, id_celda)
    if not celda:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Celda no encontrada")
    datos = payload.model_dump(exclude_unset=True)
    if "idTipo" in datos and not db.get(Tipo, datos["idTipo"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")
    for campo, valor in datos.items():
        setattr(celda, campo, valor)
    db.commit()
    db.refresh(celda)
    return celda

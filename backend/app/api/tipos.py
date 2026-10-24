from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.tipo import Tipo
from app.schemas.tipo import TipoCreate, TipoOut, TipoUpdate

router = APIRouter()


@router.get("/", response_model=list[TipoOut])
def listar_tipos(db: Session = Depends(get_db)):
    return db.query(Tipo).all()


@router.get("/{id_tipo}", response_model=TipoOut)
def obtener_tipo(id_tipo: int, db: Session = Depends(get_db)):
    tipo = db.get(Tipo, id_tipo)
    if not tipo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")
    return tipo


@router.post("/", response_model=TipoOut, status_code=status.HTTP_201_CREATED)
def crear_tipo(payload: TipoCreate, db: Session = Depends(get_db)):
    tipo = Tipo(**payload.model_dump())
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return tipo


@router.put("/{id_tipo}", response_model=TipoOut)
def actualizar_tipo(id_tipo: int, payload: TipoUpdate, db: Session = Depends(get_db)):
    tipo = db.get(Tipo, id_tipo)
    if not tipo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")
    for campo, valor in payload.model_dump().items():
        setattr(tipo, campo, valor)
    db.commit()
    db.refresh(tipo)
    return tipo

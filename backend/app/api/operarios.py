from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.operario import Operario
from app.schemas.operario import OperarioCreate, OperarioOut, OperarioUpdate

router = APIRouter()


@router.get("/", response_model=list[OperarioOut])
def listar_operarios(db: Session = Depends(get_db)):
    return db.query(Operario).all()


@router.get("/{id_operario}", response_model=OperarioOut)
def obtener_operario(id_operario: int, db: Session = Depends(get_db)):
    operario = db.get(Operario, id_operario)
    if not operario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operario no encontrado")
    return operario


@router.post("/", response_model=OperarioOut, status_code=status.HTTP_201_CREATED)
def crear_operario(payload: OperarioCreate, db: Session = Depends(get_db)):
    operario = Operario(**payload.model_dump())
    db.add(operario)
    db.commit()
    db.refresh(operario)
    return operario


@router.put("/{id_operario}", response_model=OperarioOut)
def actualizar_operario(id_operario: int, payload: OperarioUpdate, db: Session = Depends(get_db)):
    operario = db.get(Operario, id_operario)
    if not operario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operario no encontrado")
    for campo, valor in payload.model_dump().items():
        setattr(operario, campo, valor)
    db.commit()
    db.refresh(operario)
    return operario

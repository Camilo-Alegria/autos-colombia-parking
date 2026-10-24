from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate

router = APIRouter()


@router.get("/", response_model=list[ClienteOut])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).all()


@router.get("/documento/{documento}", response_model=ClienteOut)
def obtener_por_documento(documento: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.documento == documento.strip()).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return cliente


@router.get("/{id_cliente}", response_model=ClienteOut)
def obtener_cliente(id_cliente: int, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, id_cliente)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return cliente


@router.post("/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def crear_cliente(payload: ClienteCreate, db: Session = Depends(get_db)):
    existente = db.query(Cliente).filter(Cliente.documento == payload.documento).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento ya existe")
    cliente = Cliente(**payload.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.put("/{id_cliente}", response_model=ClienteOut)
def actualizar_cliente(id_cliente: int, payload: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, id_cliente)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    for campo, valor in payload.model_dump().items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return cliente

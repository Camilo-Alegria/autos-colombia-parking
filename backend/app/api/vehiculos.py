from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.detalle import armar_vehiculo_detalle
from app.core.database import get_db
from app.models.cliente import Cliente
from app.models.tipo import Tipo
from app.models.vehiculo import Vehiculo
from app.schemas.dashboard import SuscriptorCreate, VehiculoDetalleOut
from app.schemas.vehiculo import VehiculoCreate, VehiculoOut, VehiculoUpdate

router = APIRouter()


def _validar_relaciones(db: Session, id_cliente: int, id_tipo: int) -> None:
    if not db.get(Cliente, id_cliente):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    if not db.get(Tipo, id_tipo):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")


@router.get("/por-placa/{placa}", response_model=VehiculoDetalleOut)
def obtener_por_placa(placa: str, db: Session = Depends(get_db)):
    normalizada = placa.strip().upper()
    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == normalizada).first()
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    try:
        return armar_vehiculo_detalle(db, vehiculo)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/suscriptor", response_model=VehiculoDetalleOut, status_code=status.HTTP_201_CREATED)
def registrar_suscriptor(payload: SuscriptorCreate, db: Session = Depends(get_db)):
    tipo = db.get(Tipo, payload.idTipo)
    if not tipo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")

    placa = payload.placa.strip().upper()
    if db.query(Vehiculo).filter(Vehiculo.placa == placa).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La placa ya existe")

    cliente = db.query(Cliente).filter(Cliente.documento == payload.documento.strip()).first()
    if not cliente:
        cliente = Cliente(
            nombre=payload.nombre.strip(),
            documento=payload.documento.strip(),
            telefono=payload.telefono.strip(),
            correo=payload.correo.strip(),
        )
        db.add(cliente)
        db.flush()

    vehiculo = Vehiculo(
        placa=placa,
        marca=payload.marca.strip(),
        color=payload.color.strip(),
        idCliente=cliente.idCliente,
        idTipo=payload.idTipo,
    )
    db.add(vehiculo)
    db.commit()
    db.refresh(vehiculo)
    return armar_vehiculo_detalle(db, vehiculo)


@router.get("/", response_model=list[VehiculoOut])
def listar_vehiculos(db: Session = Depends(get_db)):
    return db.query(Vehiculo).all()


@router.get("/{id_vehiculo}", response_model=VehiculoOut)
def obtener_vehiculo(id_vehiculo: int, db: Session = Depends(get_db)):
    vehiculo = db.get(Vehiculo, id_vehiculo)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    return vehiculo


@router.post("/", response_model=VehiculoOut, status_code=status.HTTP_201_CREATED)
def crear_vehiculo(payload: VehiculoCreate, db: Session = Depends(get_db)):
    _validar_relaciones(db, payload.idCliente, payload.idTipo)
    existente = db.query(Vehiculo).filter(Vehiculo.placa == payload.placa).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La placa ya existe")
    vehiculo = Vehiculo(**payload.model_dump())
    db.add(vehiculo)
    db.commit()
    db.refresh(vehiculo)
    return vehiculo


@router.put("/{id_vehiculo}", response_model=VehiculoOut)
def actualizar_vehiculo(id_vehiculo: int, payload: VehiculoUpdate, db: Session = Depends(get_db)):
    vehiculo = db.get(Vehiculo, id_vehiculo)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    _validar_relaciones(db, payload.idCliente, payload.idTipo)
    for campo, valor in payload.model_dump().items():
        setattr(vehiculo, campo, valor)
    db.commit()
    db.refresh(vehiculo)
    return vehiculo

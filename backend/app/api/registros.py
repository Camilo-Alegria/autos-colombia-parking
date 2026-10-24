from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.celda import Celda
from app.models.operario import Operario
from app.models.registro_entrada_salida import RegistroEntradaSalida
from app.api.detalle import armar_vehiculo_detalle
from app.models.vehiculo import Vehiculo
from app.schemas.dashboard import ReasignarCelda, VehiculoDetalleOut
from app.schemas.registro_entrada_salida import IngresoCreate, RegistroOut

router = APIRouter()


def _calcular_tiempo_parqueo(fecha_ingreso: datetime, fecha_salida: datetime) -> int:
    segundos = (fecha_salida - fecha_ingreso).total_seconds()
    return max(0, int(segundos // 60))


@router.get("/", response_model=list[RegistroOut])
def listar_registros(db: Session = Depends(get_db)):
    return db.query(RegistroEntradaSalida).all()


@router.get("/activos", response_model=list[RegistroOut])
def listar_registros_activos(db: Session = Depends(get_db)):
    return (
        db.query(RegistroEntradaSalida)
        .filter(RegistroEntradaSalida.estadoRegistro == "ACTIVO")
        .all()
    )


@router.get("/activos/buscar", response_model=VehiculoDetalleOut)
def buscar_ingreso_activo(
    placa: str | None = None,
    celda: str | None = None,
    db: Session = Depends(get_db),
):
    vehiculo: Vehiculo | None = None
    if placa:
        vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa.strip().upper()).first()
        if not vehiculo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    elif celda:
        celda_db = db.query(Celda).filter(Celda.codigo == celda.strip().upper()).first()
        if not celda_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Celda no encontrada")
        registro = (
            db.query(RegistroEntradaSalida)
            .filter(
                RegistroEntradaSalida.idCelda == celda_db.idCelda,
                RegistroEntradaSalida.estadoRegistro == "ACTIVO",
            )
            .first()
        )
        if not registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay un ingreso activo en esa celda",
            )
        vehiculo = db.get(Vehiculo, registro.idVehiculo)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indica una placa o un código de celda",
        )

    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    detalle = armar_vehiculo_detalle(db, vehiculo)
    if not detalle.registroActivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El vehículo no tiene un ingreso activo",
        )
    return detalle


@router.get("/{id_registro}", response_model=RegistroOut)
def obtener_registro(id_registro: int, db: Session = Depends(get_db)):
    registro = db.get(RegistroEntradaSalida, id_registro)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    return registro


@router.post("/ingreso", response_model=RegistroOut, status_code=status.HTTP_201_CREATED)
def registrar_ingreso(payload: IngresoCreate, db: Session = Depends(get_db)):
    vehiculo = db.get(Vehiculo, payload.idVehiculo)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")

    operario = db.get(Operario, payload.idOperario)
    if not operario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operario no encontrado")

    activo = (
        db.query(RegistroEntradaSalida)
        .filter(
            RegistroEntradaSalida.idVehiculo == payload.idVehiculo,
            RegistroEntradaSalida.estadoRegistro == "ACTIVO",
        )
        .first()
    )
    if activo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El vehículo ya tiene un ingreso activo",
        )

    if payload.idCelda is not None:
        celda = db.get(Celda, payload.idCelda)
        if not celda:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Celda no encontrada")
        if celda.estado != "LIBRE":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La celda no está libre")
        if celda.idTipo != vehiculo.idTipo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La celda no corresponde al tipo de vehículo",
            )
    else:
        celda = (
            db.query(Celda)
            .filter(Celda.estado == "LIBRE", Celda.idTipo == vehiculo.idTipo)
            .first()
        )
        if not celda:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No hay celdas libres para el tipo de vehículo",
            )

    registro = RegistroEntradaSalida(
        fechaIngreso=datetime.now(),
        fechaSalida=None,
        estadoRegistro="ACTIVO",
        tiempoParqueo=0,
        idVehiculo=vehiculo.idVehiculo,
        idCelda=celda.idCelda,
        idOperario=operario.idOperario,
    )
    celda.estado = "OCUPADA"
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@router.post("/{id_registro}/salida", response_model=RegistroOut)
def registrar_salida(id_registro: int, db: Session = Depends(get_db)):
    registro = db.get(RegistroEntradaSalida, id_registro)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    if registro.estadoRegistro != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El registro no está activo",
        )

    fecha_salida = datetime.now()
    registro.fechaSalida = fecha_salida
    registro.tiempoParqueo = _calcular_tiempo_parqueo(registro.fechaIngreso, fecha_salida)
    registro.estadoRegistro = "FINALIZADO"

    celda = db.get(Celda, registro.idCelda)
    if celda:
        celda.estado = "LIBRE"

    db.commit()
    db.refresh(registro)
    return registro


@router.post("/{id_registro}/reasignar", response_model=RegistroOut)
def reasignar_celda(id_registro: int, payload: ReasignarCelda, db: Session = Depends(get_db)):
    registro = db.get(RegistroEntradaSalida, id_registro)
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    if registro.estadoRegistro != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede reasignar un registro activo",
        )

    nueva = db.get(Celda, payload.idCelda)
    if not nueva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Celda no encontrada")
    if nueva.idCelda == registro.idCelda:
        return registro
    if nueva.estado != "LIBRE":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La celda no está libre")

    vehiculo = db.get(Vehiculo, registro.idVehiculo)
    if vehiculo and nueva.idTipo != vehiculo.idTipo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La celda no corresponde al tipo de vehículo",
        )

    anterior = db.get(Celda, registro.idCelda)
    if anterior:
        anterior.estado = "LIBRE"
    nueva.estado = "OCUPADA"
    registro.idCelda = nueva.idCelda
    db.commit()
    db.refresh(registro)
    return registro

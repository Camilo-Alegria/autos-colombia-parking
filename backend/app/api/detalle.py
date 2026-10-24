from sqlalchemy.orm import Session

from app.models.celda import Celda
from app.models.cliente import Cliente
from app.models.registro_entrada_salida import RegistroEntradaSalida
from app.models.tipo import Tipo
from app.models.vehiculo import Vehiculo
from app.schemas.dashboard import (
    CeldaDetalleOut,
    ClienteResumen,
    RegistroResumen,
    TipoResumen,
    VehiculoDetalleOut,
    VehiculoResumen,
)


def registro_activo_vehiculo(db: Session, id_vehiculo: int) -> RegistroEntradaSalida | None:
    return (
        db.query(RegistroEntradaSalida)
        .filter(
            RegistroEntradaSalida.idVehiculo == id_vehiculo,
            RegistroEntradaSalida.estadoRegistro == "ACTIVO",
        )
        .first()
    )


def armar_celda_detalle(
    celda: Celda,
    tipo: Tipo | None = None,
    registro: RegistroEntradaSalida | None = None,
    vehiculo: Vehiculo | None = None,
    cliente: Cliente | None = None,
) -> CeldaDetalleOut:
    return CeldaDetalleOut(
        idCelda=celda.idCelda,
        codigo=celda.codigo,
        estado=celda.estado,
        idTipo=celda.idTipo,
        tipo=TipoResumen.model_validate(tipo) if tipo else None,
        registro=RegistroResumen.model_validate(registro) if registro else None,
        vehiculo=VehiculoResumen.model_validate(vehiculo) if vehiculo else None,
        cliente=ClienteResumen.model_validate(cliente) if cliente else None,
    )


def armar_vehiculo_detalle(db: Session, vehiculo: Vehiculo) -> VehiculoDetalleOut:
    cliente = db.get(Cliente, vehiculo.idCliente)
    tipo = db.get(Tipo, vehiculo.idTipo)
    if not cliente or not tipo:
        raise ValueError("El vehículo no tiene cliente o tipo asociado")
    registro = registro_activo_vehiculo(db, vehiculo.idVehiculo)
    celda = db.get(Celda, registro.idCelda) if registro else None
    return VehiculoDetalleOut(
        vehiculo=VehiculoResumen.model_validate(vehiculo),
        cliente=ClienteResumen.model_validate(cliente),
        tipo=TipoResumen.model_validate(tipo),
        celda=armar_celda_detalle(celda, tipo, registro, vehiculo, cliente) if celda else None,
        registroActivo=RegistroResumen.model_validate(registro) if registro else None,
    )

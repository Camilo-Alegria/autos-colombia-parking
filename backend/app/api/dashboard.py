from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.detalle import armar_celda_detalle
from app.core.database import get_db
from app.models.celda import Celda
from app.models.cliente import Cliente
from app.models.operario import Operario
from app.models.registro_entrada_salida import RegistroEntradaSalida
from app.models.tipo import Tipo
from app.models.vehiculo import Vehiculo
from app.schemas.dashboard import DashboardOut

router = APIRouter()


@router.get("/", response_model=DashboardOut)
def obtener_dashboard(db: Session = Depends(get_db)):
    tipos = {tipo.idTipo: tipo for tipo in db.query(Tipo).all()}
    vehiculos = {vehiculo.idVehiculo: vehiculo for vehiculo in db.query(Vehiculo).all()}
    clientes = {cliente.idCliente: cliente for cliente in db.query(Cliente).all()}
    activos = (
        db.query(RegistroEntradaSalida)
        .filter(RegistroEntradaSalida.estadoRegistro == "ACTIVO")
        .all()
    )
    activos_por_celda = {registro.idCelda: registro for registro in activos}
    celdas = db.query(Celda).order_by(Celda.codigo).all()
    operario = db.query(Operario).order_by(Operario.idOperario).first()

    detalle_celdas = []
    for celda in celdas:
        registro = activos_por_celda.get(celda.idCelda)
        vehiculo = vehiculos.get(registro.idVehiculo) if registro else None
        cliente = clientes.get(vehiculo.idCliente) if vehiculo else None
        detalle_celdas.append(
            armar_celda_detalle(
                celda,
                tipos.get(celda.idTipo),
                registro,
                vehiculo,
                cliente,
            )
        )

    return DashboardOut(
        vehiculosRegistrados=len(vehiculos),
        vehiculosIngresados=len(activos),
        celdasDisponibles=sum(1 for celda in celdas if celda.estado == "LIBRE"),
        defaultOperarioId=operario.idOperario if operario else None,
        celdas=detalle_celdas,
    )

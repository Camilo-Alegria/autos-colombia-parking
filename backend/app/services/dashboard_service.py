from sqlalchemy.orm import Session

from app.api.detalle import armar_celda_detalle
from app.models.celda import Celda
from app.models.cliente import Cliente
from app.models.registro_entrada_salida import RegistroEntradaSalida
from app.models.tipo import Tipo
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.dashboard import DashboardOut


class DashboardService:
    def obtener_dashboard(self, db: Session) -> DashboardOut:
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
        operario = db.query(Usuario).order_by(Usuario.id_usuario).first()

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
            celdasDisponibles=sum(1 for celda in celdas if celda.estado == "LIBRE" and celda.activo),
            defaultOperarioId=operario.id_usuario if operario else None,
            celdas=detalle_celdas,
        )


dashboard_service = DashboardService()

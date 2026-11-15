from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.tipo import Tipo
from app.models.vehiculo import Vehiculo
from app.repositories.cliente_repository import cliente_repo
from app.repositories.vehiculo_repository import vehiculo_repo
from app.schemas.dashboard import SuscriptorCreate, VehiculoDetalleOut
from app.schemas.vehiculo import VehiculoUpdate
from app.services.auditoria_service import auditoria_service
from app.api.detalle import armar_vehiculo_detalle


class VehiculoService:
    def registrar_suscriptor(self, db: Session, payload: SuscriptorCreate, current_user, ip: str | None = None) -> VehiculoDetalleOut:
        tipo = db.get(Tipo, payload.idTipo)
        if not tipo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")

        placa = payload.placa.strip().upper()
        if vehiculo_repo.obtener_por_placa(db, placa):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La placa ya existe")

        cliente = cliente_repo.obtener_por_documento(db, payload.documento)
        if not cliente:
            cliente = cliente_repo.crear_cliente(
                db,
                {
                    "nombre": payload.nombre.strip(),
                    "documento": payload.documento.strip(),
                    "telefono": payload.telefono.strip(),
                    "correo": payload.correo.strip(),
                },
            )

        vehiculo = vehiculo_repo.crear_vehiculo(
            db,
            {
                "placa": placa,
                "marca": payload.marca.strip(),
                "modelo": payload.modelo.strip(),
                "color": payload.color.strip(),
                "estado_pago": payload.estado_pago.strip().upper(),
                "idCliente": cliente.idCliente,
                "idTipo": payload.idTipo,
            },
        )
        db.commit()
        db.refresh(vehiculo)

        auditoria_service.registrar_accion(
            db,
            accion="CREAR_SUSCRIPTOR",
            detalles=f"Registrado vehículo {vehiculo.placa} y propietario {cliente.nombre}",
            usuario=current_user,
            ip=ip,
        )
        return armar_vehiculo_detalle(db, vehiculo)

    def actualizar_vehiculo(self, db: Session, id_vehiculo: int, payload: VehiculoUpdate, current_user, ip: str | None = None) -> Vehiculo:
        vehiculo = vehiculo_repo.obtener_por_id(db, id_vehiculo)
        if not vehiculo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")

        data = payload.model_dump(exclude_unset=True)
        if "idCliente" in data and not db.get(Cliente, data["idCliente"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
        if "idTipo" in data and not db.get(Tipo, data["idTipo"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")
        if "placa" in data:
            data["placa"] = data["placa"].strip().upper()

        updated = vehiculo_repo.actualizar_vehiculo(db, vehiculo, data)
        auditoria_service.registrar_accion(
            db,
            accion="ACTUALIZAR_VEHICULO",
            detalles=f"Actualizado vehículo {updated.placa}",
            usuario=current_user,
            ip=ip,
        )
        return updated


vehiculo_service = VehiculoService()

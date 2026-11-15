from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.websocket_manager import ws_manager
from app.models.registro_entrada_salida import RegistroEntradaSalida
from app.models.vehiculo import Vehiculo
from app.repositories.celda_repository import celda_repo
from app.repositories.registro_repository import registro_repo
from app.repositories.vehiculo_repository import vehiculo_repo
from app.schemas.dashboard import ReasignarCelda
from app.schemas.registro_entrada_salida import IngresoCreate
from app.services.auditoria_service import auditoria_service


class ParqueoService:
    def _calcular_tiempo_parqueo(self, fecha_ingreso: datetime, fecha_salida: datetime) -> int:
        segundos = (fecha_salida - fecha_ingreso).total_seconds()
        return max(0, int(segundos // 60))

    async def registrar_ingreso(self, db: Session, payload: IngresoCreate, current_user, ip: str | None = None) -> RegistroEntradaSalida:
        vehiculo = vehiculo_repo.obtener_por_id(db, payload.idVehiculo)
        if not vehiculo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")

        if getattr(vehiculo, "estado_pago", "AL_DIA").upper() == "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El vehículo tiene la mensualidad PENDIENTE. No se permite el ingreso al parqueadero.",
            )

        if registro_repo.obtener_activo_por_vehiculo(db, vehiculo.idVehiculo):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El vehículo ya tiene un ingreso activo en el parqueadero",
            )

        celda = None
        if payload.idCelda is not None:
            celda = celda_repo.obtener_por_id(db, payload.idCelda, for_update=True)
            if not celda:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Celda no encontrada")
            if celda.estado != "LIBRE" or not celda.activo:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="La celda ya fue ocupada, reservada o está inactiva por otro operario.",
                )
            if celda.idTipo != vehiculo.idTipo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La celda no corresponde al tipo de vehículo (Carro/Moto).",
                )
        else:
            celda = celda_repo.obtener_libre_por_tipo(db, vehiculo.idTipo, for_update=True)
            if not celda:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No hay celdas libres disponibles para el tipo de vehículo.",
                )

        celda.estado = "OCUPADA"
        registro = registro_repo.crear_registro(
            db,
            {
                "fechaIngreso": datetime.now(),
                "fechaSalida": None,
                "estadoRegistro": "ACTIVO",
                "tiempoParqueo": 0,
                "idVehiculo": vehiculo.idVehiculo,
                "idCelda": celda.idCelda,
                "idOperario": current_user.id_usuario,
            },
        )
        db.commit()
        db.refresh(registro)

        auditoria_service.registrar_accion(
            db,
            accion="INGRESO_VEHICULO",
            detalles=f"Vehículo {vehiculo.placa} ingresó a celda {celda.codigo}",
            usuario=current_user,
            ip=ip,
        )
        await ws_manager.broadcast({"event": "celda_actualizada", "codigo": celda.codigo})
        return registro

    async def registrar_salida(self, db: Session, id_registro: int, current_user, ip: str | None = None) -> RegistroEntradaSalida:
        registro = registro_repo.obtener_por_id(db, id_registro, for_update=True)
        if not registro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
        if registro.estadoRegistro != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El registro no está activo",
            )

        fecha_salida = datetime.now()
        registro.fechaSalida = fecha_salida
        registro.tiempoParqueo = self._calcular_tiempo_parqueo(registro.fechaIngreso, fecha_salida)
        registro.estadoRegistro = "FINALIZADO"

        celda = celda_repo.obtener_por_id(db, registro.idCelda, for_update=True)
        if celda:
            celda.estado = "LIBRE"

        db.commit()
        db.refresh(registro)

        vehiculo = vehiculo_repo.obtener_por_id(db, registro.idVehiculo)
        placa_str = vehiculo.placa if vehiculo else str(registro.idVehiculo)
        celda_str = celda.codigo if celda else str(registro.idCelda)

        auditoria_service.registrar_accion(
            db,
            accion="SALIDA_VEHICULO",
            detalles=f"Vehículo {placa_str} salió de celda {celda_str}. Permanencia: {registro.tiempoParqueo} min",
            usuario=current_user,
            ip=ip,
        )
        if celda:
            await ws_manager.broadcast({"event": "celda_actualizada", "codigo": celda.codigo})
        return registro

    async def reasignar_celda(self, db: Session, id_registro: int, payload: ReasignarCelda, current_user, ip: str | None = None) -> RegistroEntradaSalida:
        registro = registro_repo.obtener_por_id(db, id_registro, for_update=True)
        if not registro:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
        if registro.estadoRegistro != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se puede reasignar un registro activo",
            )

        nueva = celda_repo.obtener_por_id(db, payload.idCelda, for_update=True)
        if not nueva:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Celda no encontrada")
        if nueva.idCelda == registro.idCelda:
            return registro
        if nueva.estado != "LIBRE" or not nueva.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La celda destino ya fue ocupada, reservada o está inactiva por otro operario.",
            )

        vehiculo = vehiculo_repo.obtener_por_id(db, registro.idVehiculo)
        if vehiculo and nueva.idTipo != vehiculo.idTipo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La celda no corresponde al tipo de vehículo.",
            )

        anterior = celda_repo.obtener_por_id(db, registro.idCelda, for_update=True)
        if anterior:
            anterior.estado = "LIBRE"
        nueva.estado = "OCUPADA"
        registro.idCelda = nueva.idCelda
        db.commit()
        db.refresh(registro)

        auditoria_service.registrar_accion(
            db,
            accion="REASIGNACION_CELDA",
            detalles=f"Vehículo {vehiculo.placa if vehiculo else ''} reasignado de {anterior.codigo if anterior else ''} a {nueva.codigo}",
            usuario=current_user,
            ip=ip,
        )
        if anterior:
            await ws_manager.broadcast({"event": "celda_actualizada", "codigo": anterior.codigo})
        await ws_manager.broadcast({"event": "celda_actualizada", "codigo": nueva.codigo})
        return registro


parqueo_service = ParqueoService()


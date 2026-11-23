from datetime import date, datetime
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional, hash_password
from app.models.cliente import Cliente
from app.models.pago import Pago
from app.models.tipo import Tipo
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.schemas.pago import (
    ClienteEstadoCuentaOut,
    PagoOut,
    PagoPresencialCreate,
    VehiculoClienteCreate,
    VehiculoEstadoCuentaOut,
)
from app.services.auditoria_service import auditoria_service
from app.services.pagos_service import (
    avanzar_mes_vencimiento,
    calcular_estado_semaforo,
    obtener_tarifa_vehiculo,
)

router = APIRouter()


class PagoOnlinePreferenciaCreate(BaseModel):
    placa: str


class PagoOnlineConfirmarCreate(BaseModel):
    placa: str
    payment_id: str | int


@router.post("/vehiculos-clientes", response_model=VehiculoEstadoCuentaOut, status_code=status.HTTP_201_CREATED)
def registrar_vehiculo_cliente(
    payload: VehiculoClienteCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: Usuario | None = Depends(get_current_user_optional),
):
    placa_upper = payload.placa.strip().upper()
    existing_vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa_upper).first()
    if existing_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La placa del vehículo ya se encuentra registrada",
        )

    tipo_db = db.get(Tipo, payload.idTipo)
    if not tipo_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de vehículo no encontrado",
        )

    documento_clean = payload.cedula.strip()

    # 1. Obtener o crear Usuario CLIENTE sin modificar datos si ya existe
    usuario_cliente = db.query(Usuario).filter(Usuario.documento == documento_clean).first()
    if not usuario_cliente:
        usuario_cliente = Usuario(
            nombre=payload.nombre.strip(),
            documento=documento_clean,
            usuario=documento_clean,
            password_hash=hash_password(payload.password),
            rol="CLIENTE",
            activo=True,
        )
        db.add(usuario_cliente)
        db.flush()

    # 2. Obtener o crear Cliente sin modificar datos si ya existe
    cliente_legacy = db.query(Cliente).filter(Cliente.documento == documento_clean).first()
    if not cliente_legacy:
        cliente_legacy = Cliente(
            nombre=payload.nombre.strip(),
            documento=documento_clean,
            telefono=payload.telefono.strip(),
            correo=f"{documento_clean}@autoscolombia.com",
        )
        db.add(cliente_legacy)
        db.flush()

    hoy = date.today()
    dia_corte = hoy.day
    fecha_vencimiento = avanzar_mes_vencimiento(None, dia_corte)

    nuevo_vehiculo = Vehiculo(
        placa=placa_upper,
        marca=payload.marca.strip(),
        modelo=payload.modelo.strip(),
        color=payload.color.strip(),
        estado_pago="AL_DIA",
        dia_corte=dia_corte,
        fecha_vencimiento=fecha_vencimiento,
        id_usuario_cliente=usuario_cliente.id_usuario,
        idCliente=cliente_legacy.idCliente,
        idTipo=tipo_db.idTipo,
    )
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)

    ip_client = request.client.host if request and request.client else "127.0.0.1"
    auditoria_service.registrar_accion(
        db=db,
        accion="REGISTRO_VEHICULO_CLIENTE",
        detalles=f"Registro de vehículo cliente placa {placa_upper} asociado a cedula {documento_clean}",
        usuario=usuario_actual or usuario_cliente,
        ip=ip_client,
    )

    tarifa = obtener_tarifa_vehiculo(db, nuevo_vehiculo)
    estado_semaforo = calcular_estado_semaforo(nuevo_vehiculo.fecha_vencimiento)

    return VehiculoEstadoCuentaOut(
        idVehiculo=nuevo_vehiculo.idVehiculo,
        placa=nuevo_vehiculo.placa,
        marca=nuevo_vehiculo.marca,
        modelo=nuevo_vehiculo.modelo,
        color=nuevo_vehiculo.color,
        dia_corte=nuevo_vehiculo.dia_corte,
        fecha_vencimiento=nuevo_vehiculo.fecha_vencimiento,
        estado_pago=nuevo_vehiculo.estado_pago,
        estado_semaforo=estado_semaforo,
        tarifa=tarifa,
        historial_pagos=[],
    )


@router.get("/placa/{placa}", response_model=VehiculoEstadoCuentaOut)
def consultar_vehiculo_placa(placa: str, db: Session = Depends(get_db)):
    placa_upper = placa.strip().upper()
    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa_upper).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado",
        )

    tarifa = obtener_tarifa_vehiculo(db, vehiculo)
    estado_semaforo = calcular_estado_semaforo(vehiculo.fecha_vencimiento)
    vehiculo.estado_pago = "AL_DIA" if estado_semaforo in ("AL_DIA", "PROXIMO_A_VENCER") else "VENCIDO"
    db.commit()

    pagos_db = db.query(Pago).filter(Pago.id_vehiculo == vehiculo.idVehiculo).order_by(Pago.fecha_pago.desc()).all()

    return VehiculoEstadoCuentaOut(
        idVehiculo=vehiculo.idVehiculo,
        placa=vehiculo.placa,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        color=vehiculo.color,
        dia_corte=vehiculo.dia_corte,
        fecha_vencimiento=vehiculo.fecha_vencimiento,
        estado_pago=vehiculo.estado_pago,
        estado_semaforo=estado_semaforo,
        tarifa=tarifa,
        historial_pagos=[PagoOut.model_validate(p) for p in pagos_db],
    )


@router.get("/vehiculos-clientes/propietario/{cedula}")
def consultar_propietario(cedula: str, db: Session = Depends(get_db)):
    cliente_legacy = db.query(Cliente).filter(Cliente.documento == cedula.strip()).first()
    if cliente_legacy:
        return {
            "existe": True,
            "nombre": cliente_legacy.nombre,
            "telefono": cliente_legacy.telefono or "",
        }

    usuario_cliente = db.query(Usuario).filter(Usuario.documento == cedula.strip()).first()
    if usuario_cliente:
        return {
            "existe": True,
            "nombre": usuario_cliente.nombre,
            "telefono": "",
        }

    return {"existe": False, "nombre": "", "telefono": ""}


@router.post("/presencial", response_model=PagoOut, status_code=status.HTTP_201_CREATED)
def registrar_pago_presencial(
    payload: PagoPresencialCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    placa_upper = payload.placa.strip().upper()
    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa_upper).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado",
        )

    estado_semaforo = calcular_estado_semaforo(vehiculo.fecha_vencimiento)
    if estado_semaforo == "AL_DIA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El vehículo ya se encuentra al día, no requiere pago en este momento",
        )

    monto = obtener_tarifa_vehiculo(db, vehiculo)
    nuevo_pago = Pago(
        id_vehiculo=vehiculo.idVehiculo,
        monto=monto,
        metodo_pago="PRESENCIAL",
        referencia_pasarela=None,
        estado="APROBADO",
        fecha_pago=datetime.now(),
    )
    db.add(nuevo_pago)

    dia_corte = vehiculo.dia_corte or (vehiculo.fecha_vencimiento.day if vehiculo.fecha_vencimiento else date.today().day)
    vehiculo.dia_corte = dia_corte
    vehiculo.fecha_vencimiento = avanzar_mes_vencimiento(vehiculo.fecha_vencimiento, dia_corte)
    vehiculo.estado_pago = "AL_DIA"

    db.commit()
    db.refresh(nuevo_pago)
    db.refresh(vehiculo)

    ip_client = request.client.host if request and request.client else "127.0.0.1"
    auditoria_service.registrar_accion(
        db=db,
        accion="PAGO_PRESENCIAL",
        detalles=f"Pago presencial aprobado por monto {monto} para vehículo {placa_upper}",
        usuario=usuario_actual,
        ip=ip_client,
    )

    return PagoOut.model_validate(nuevo_pago)


@router.get("/cliente/estado-cuenta", response_model=ClienteEstadoCuentaOut)
def obtener_estado_cuenta_cliente(
    cedula: str | None = None,
    db: Session = Depends(get_db),
    usuario_actual: Usuario | None = Depends(get_current_user_optional),
):
    target_cedula = cedula
    if not target_cedula and usuario_actual:
        target_cedula = usuario_actual.documento

    if not target_cedula:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar la cédula o estar autenticado como cliente",
        )

    usuario_cliente = db.query(Usuario).filter(Usuario.documento == target_cedula.strip()).first()
    cliente_legacy = db.query(Cliente).filter(Cliente.documento == target_cedula.strip()).first()

    if not usuario_cliente and not cliente_legacy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )

    nombre = usuario_cliente.nombre if usuario_cliente else cliente_legacy.nombre
    cedula_val = target_cedula.strip()

    vehiculos_db = []
    if usuario_cliente:
        vehiculos_db = db.query(Vehiculo).filter(Vehiculo.id_usuario_cliente == usuario_cliente.id_usuario).all()
    if not vehiculos_db and cliente_legacy:
        vehiculos_db = db.query(Vehiculo).filter(Vehiculo.idCliente == cliente_legacy.idCliente).all()

    vehiculos_out = []
    for v in vehiculos_db:
        tarifa = obtener_tarifa_vehiculo(db, v)
        estado_semaforo = calcular_estado_semaforo(v.fecha_vencimiento)
        v.estado_pago = "AL_DIA" if estado_semaforo in ("AL_DIA", "PROXIMO_A_VENCER") else "VENCIDO"
        db.commit()

        pagos_db = db.query(Pago).filter(Pago.id_vehiculo == v.idVehiculo).order_by(Pago.fecha_pago.desc()).all()

        vehiculos_out.append(
            VehiculoEstadoCuentaOut(
                idVehiculo=v.idVehiculo,
                placa=v.placa,
                marca=v.marca,
                modelo=v.modelo,
                color=v.color,
                dia_corte=v.dia_corte,
                fecha_vencimiento=v.fecha_vencimiento,
                estado_pago=v.estado_pago,
                estado_semaforo=estado_semaforo,
                tarifa=tarifa,
                historial_pagos=[PagoOut.model_validate(p) for p in pagos_db],
            )
        )

    return ClienteEstadoCuentaOut(
        cedula=cedula_val,
        nombre=nombre,
        vehiculos=vehiculos_out,
    )


@router.post("/online/preferencia")
def crear_preferencia_pago_online(
    payload: PagoOnlinePreferenciaCreate,
    db: Session = Depends(get_db),
):
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="STRIPE_SECRET_KEY no está configurada en el archivo .env",
        )

    placa_upper = payload.placa.strip().upper()
    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa_upper).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado",
        )

    estado_semaforo = calcular_estado_semaforo(vehiculo.fecha_vencimiento)
    if estado_semaforo == "AL_DIA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El vehículo ya se encuentra al día",
        )

    tarifa = obtener_tarifa_vehiculo(db, vehiculo)
    frontend_base = settings.frontend_url.rstrip("/")

    stripe_payload = {
        "mode": "payment",
        "client_reference_id": placa_upper,
        "success_url": f"{frontend_base}/cliente?status=approved&payment_id={{CHECKOUT_SESSION_ID}}&external_reference={placa_upper}",
        "cancel_url": f"{frontend_base}/cliente?status=cancelled",
        "line_items[0][price_data][currency]": "cop",
        "line_items[0][price_data][product_data][name]": f"Mensualidad Parqueadero Autos Colombia - {placa_upper}",
        "line_items[0][price_data][unit_amount]": int(tarifa) * 100,
        "line_items[0][quantity]": 1,
    }

    response = httpx.post(
        "https://api.stripe.com/v1/checkout/sessions",
        data=stripe_payload,
        auth=(settings.stripe_secret_key, ""),
        timeout=15.0,
    )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al crear sesión de pago en Stripe: {response.text}",
        )

    data = response.json()
    return {
        "init_point": data.get("url"),
        "preference_id": data.get("id"),
    }


@router.post("/online/confirmar", response_model=PagoOut, status_code=status.HTTP_201_CREATED)
def confirmar_pago_online(
    payload: PagoOnlineConfirmarCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: Usuario | None = Depends(get_current_user_optional),
):
    placa_upper = payload.placa.strip().upper()
    ref_str = str(payload.payment_id).strip()

    # Evitar duplicados si el usuario recarga la URL de retorno
    pago_existente = db.query(Pago).filter(Pago.referencia_pasarela == ref_str).first()
    if pago_existente:
        return PagoOut.model_validate(pago_existente)

    # Verificar el estado real de la sesión en Stripe si es un ID de sesión
    if settings.stripe_secret_key and ref_str.startswith("cs_"):
        verify_res = httpx.get(
            f"https://api.stripe.com/v1/checkout/sessions/{ref_str}",
            auth=(settings.stripe_secret_key, ""),
            timeout=15.0,
        )
        if verify_res.status_code == 200:
            session_data = verify_res.json()
            if session_data.get("payment_status") != "paid":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El pago aún no figura como aprobado en Stripe",
                )

    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa_upper).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado",
        )

    monto = obtener_tarifa_vehiculo(db, vehiculo)
    nuevo_pago = Pago(
        id_vehiculo=vehiculo.idVehiculo,
        monto=monto,
        metodo_pago="ONLINE",
        referencia_pasarela=ref_str,
        estado="APROBADO",
        fecha_pago=datetime.now(),
    )
    db.add(nuevo_pago)

    dia_corte = vehiculo.dia_corte or (vehiculo.fecha_vencimiento.day if vehiculo.fecha_vencimiento else date.today().day)
    vehiculo.dia_corte = dia_corte
    vehiculo.fecha_vencimiento = avanzar_mes_vencimiento(vehiculo.fecha_vencimiento, dia_corte)
    vehiculo.estado_pago = "AL_DIA"

    db.commit()
    db.refresh(nuevo_pago)
    db.refresh(vehiculo)

    ip_client = request.client.host if request and request.client else "127.0.0.1"
    auditoria_service.registrar_accion(
        db=db,
        accion="PAGO_ONLINE",
        detalles=f"Pago online aprobado por monto {monto} para vehículo {placa_upper} (Ref: {ref_str})",
        usuario=usuario_actual,
        ip=ip_client,
    )

    return PagoOut.model_validate(nuevo_pago)
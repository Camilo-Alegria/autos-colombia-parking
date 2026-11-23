from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from app.models.vehiculo import Vehiculo


def calcular_estado_semaforo(fecha_vencimiento: date | None) -> str:
    if not fecha_vencimiento:
        return "SE_REQUIERE_PAGO"
    
    hoy = date.today()
    if fecha_vencimiento < hoy:
        return "SE_REQUIERE_PAGO"
    
    dias_restantes = (fecha_vencimiento - hoy).days
    if dias_restantes > 5:
        return "AL_DIA"
    else:
        return "PROXIMO_A_VENCER"


def obtener_tarifa_vehiculo(db: Session, vehiculo: Vehiculo) -> int:
    # Tarifas fijas: Carro = 250000, Moto = 100000
    if vehiculo.tipo and vehiculo.tipo.nombre:
        nombre_tipo = vehiculo.tipo.nombre.strip().lower()
        if "moto" in nombre_tipo:
            return 100_000
    return 250_000


def avanzar_mes_vencimiento(fecha_actual: date | None, dia_corte: int) -> date:
    hoy = date.today()
    if not fecha_actual or fecha_actual < hoy:
        # Si estaba vencido o no tiene fecha, avanza al próximo corte mensual correspondiente a partir de hoy o fecha actual
        base = fecha_actual if fecha_actual and fecha_actual >= hoy else hoy
    else:
        base = fecha_actual

    # Suma 1 mes manteniendo fijo el dia_corte original
    nueva_fecha = base + relativedelta(months=1)
    # Asegurar que el día sea el dia_corte o el último día válido del mes
    try:
        nueva_fecha = nueva_fecha.replace(day=dia_corte)
    except ValueError:
        # Si el día del corte (ej. 31) no existe en ese mes, tomar el último día del mes
        next_month = nueva_fecha.replace(day=1) + relativedelta(months=1)
        nueva_fecha = next_month - timedelta(days=1)
    
    return nueva_fecha

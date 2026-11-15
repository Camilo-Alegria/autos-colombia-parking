from fastapi import APIRouter

from app.api import (
    auditoria,
    auth,
    celdas,
    clientes,
    dashboard,
    operarios,
    registros,
    tipos,
    usuarios,
    vehiculos,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["auditoria"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(tipos.router, prefix="/tipos", tags=["tipos"])
api_router.include_router(vehiculos.router, prefix="/vehiculos", tags=["vehiculos"])
api_router.include_router(celdas.router, prefix="/celdas", tags=["celdas"])
api_router.include_router(operarios.router, prefix="/operarios", tags=["operarios"])
api_router.include_router(registros.router, prefix="/registros", tags=["registros"])


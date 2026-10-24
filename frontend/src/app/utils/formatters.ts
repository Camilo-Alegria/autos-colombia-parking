import { HttpErrorResponse } from '@angular/common/http';

export function formatTarifa(valor: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(valor);
}

export function formatFecha(valor: string | null | undefined): string {
  if (!valor) {
    return '—';
  }
  return new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'short',
    timeStyle: 'medium',
  }).format(new Date(valor));
}

export function calcularPermanencia(fechaIngreso: string, hasta: Date = new Date()): {
  horas: number;
  minutos: number;
  texto: string;
  totalMinutos: number;
} {
  const ms = Math.max(0, hasta.getTime() - new Date(fechaIngreso).getTime());
  const totalMinutos = Math.floor(ms / 60_000);
  const horas = Math.floor(totalMinutos / 60);
  const minutos = totalMinutos % 60;
  return {
    horas,
    minutos,
    totalMinutos,
    texto: `${horas} h ${minutos.toString().padStart(2, '0')} min`,
  };
}

export function mensajeApi(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    const detalle = error.error?.detail;
    if (typeof detalle === 'string' && detalle.trim()) {
      return detalle;
    }
    if (Array.isArray(detalle) && detalle.length) {
      return detalle
        .map((item: { msg?: string }) => item.msg ?? JSON.stringify(item))
        .join('. ');
    }
    if (error.status === 0) {
      return 'No hay conexión con el backend. Confirma que FastAPI esté en el puerto 8000.';
    }
    return error.statusText || 'Error de comunicación con la API.';
  }
  return 'Ocurrió un error inesperado.';
}

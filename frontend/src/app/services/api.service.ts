import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import {
  Celda,
  ClienteResumen,
  ClienteUpdate,
  Dashboard,
  IngresoCreate,
  RegistroResumen,
  SuscriptorCreate,
  Tipo,
  VehiculoDetalle,
  VehiculoUpdate,
} from '../models/parking.models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api';

  obtenerDashboard(): Observable<Dashboard> {
    return this.http.get<Dashboard>(`${this.base}/dashboard/`);
  }

  listarTipos(): Observable<Tipo[]> {
    return this.http.get<Tipo[]>(`${this.base}/tipos/`);
  }

  celdasDisponibles(idTipo?: number): Observable<Celda[]> {
    let params = new HttpParams();
    if (idTipo != null) {
      params = params.set('id_tipo', idTipo);
    }
    return this.http.get<Celda[]>(`${this.base}/celdas/disponibles`, { params });
  }

  buscarPorPlaca(placa: string): Observable<VehiculoDetalle> {
    return this.http.get<VehiculoDetalle>(
      `${this.base}/vehiculos/por-placa/${encodeURIComponent(placa.trim().toUpperCase())}`,
    );
  }

  registrarSuscriptor(payload: SuscriptorCreate): Observable<VehiculoDetalle> {
    return this.http.post<VehiculoDetalle>(`${this.base}/vehiculos/suscriptor`, payload);
  }

  registrarIngreso(payload: IngresoCreate): Observable<RegistroResumen> {
    return this.http.post<RegistroResumen>(`${this.base}/registros/ingreso`, payload);
  }

  buscarIngresoActivo(placa?: string, celda?: string): Observable<VehiculoDetalle> {
    let params = new HttpParams();
    if (placa?.trim()) {
      params = params.set('placa', placa.trim().toUpperCase());
    }
    if (celda?.trim()) {
      params = params.set('celda', celda.trim().toUpperCase());
    }
    return this.http.get<VehiculoDetalle>(`${this.base}/registros/activos/buscar`, { params });
  }

  registrarSalida(idRegistro: number): Observable<RegistroResumen> {
    return this.http.post<RegistroResumen>(`${this.base}/registros/${idRegistro}/salida`, {});
  }

  reasignarCelda(idRegistro: number, idCelda: number): Observable<RegistroResumen> {
    return this.http.post<RegistroResumen>(`${this.base}/registros/${idRegistro}/reasignar`, {
      idCelda,
    });
  }

  actualizarCliente(idCliente: number, payload: ClienteUpdate): Observable<ClienteResumen> {
    return this.http.put<ClienteResumen>(`${this.base}/clientes/${idCliente}`, payload);
  }

  actualizarVehiculo(idVehiculo: number, payload: VehiculoUpdate): Observable<VehiculoUpdate & { idVehiculo: number }> {
    return this.http.put<VehiculoUpdate & { idVehiculo: number }>(
      `${this.base}/vehiculos/${idVehiculo}`,
      payload,
    );
  }
}

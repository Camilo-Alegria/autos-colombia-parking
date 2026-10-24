import { Injectable, computed, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { CeldaDetalle, Dashboard, Tipo } from '../models/parking.models';
import { mensajeApi } from '../utils/formatters';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class ParkingStore {
  private readonly api = inject(ApiService);

  readonly dashboard = signal<Dashboard | null>(null);
  readonly tipos = signal<Tipo[]>([]);
  readonly cargando = signal(false);
  readonly aviso = signal<{ tipo: 'ok' | 'error'; texto: string } | null>(null);

  readonly celdasCarro = computed(
    () => this.dashboard()?.celdas.filter((celda) => celda.codigo.startsWith('C')) ?? [],
  );
  readonly celdasMoto = computed(
    () => this.dashboard()?.celdas.filter((celda) => celda.codigo.startsWith('M')) ?? [],
  );

  async cargarTodo(): Promise<void> {
    this.cargando.set(true);
    try {
      const [dashboard, tipos] = await Promise.all([
        firstValueFrom(this.api.obtenerDashboard()),
        firstValueFrom(this.api.listarTipos()),
      ]);
      this.dashboard.set(dashboard);
      this.tipos.set(tipos);
    } catch (error) {
      this.aviso.set({ tipo: 'error', texto: mensajeApi(error) });
    } finally {
      this.cargando.set(false);
    }
  }

  async refrescarDashboard(): Promise<void> {
    try {
      this.dashboard.set(await firstValueFrom(this.api.obtenerDashboard()));
    } catch (error) {
      this.aviso.set({ tipo: 'error', texto: mensajeApi(error) });
    }
  }

  marcarOk(texto: string): void {
    this.aviso.set({ tipo: 'ok', texto });
  }

  marcarError(texto: string): void {
    this.aviso.set({ tipo: 'error', texto });
  }

  limpiarAviso(): void {
    this.aviso.set(null);
  }

  celdaPorCodigo(codigo: string): CeldaDetalle | undefined {
    return this.dashboard()?.celdas.find(
      (celda) => celda.codigo.toUpperCase() === codigo.trim().toUpperCase(),
    );
  }
}

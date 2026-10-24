import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { VehiculoDetalle } from '../models/parking.models';
import { ApiService } from '../services/api.service';
import { ParkingStore } from '../services/parking.store';
import { calcularPermanencia, formatFecha, mensajeApi } from '../utils/formatters';

@Component({
  selector: 'app-salida-page',
  imports: [FormsModule],
  templateUrl: './salida.page.html',
})
export class SalidaPage implements OnInit, OnDestroy {
  private readonly api = inject(ApiService);
  protected readonly store = inject(ParkingStore);
  protected readonly formatFecha = formatFecha;

  criterio = '';
  modo: 'placa' | 'celda' = 'placa';
  detalle = signal<VehiculoDetalle | null>(null);
  permanencia = signal({ horas: 0, minutos: 0, texto: '0 h 00 min', totalMinutos: 0 });
  enviando = signal(false);
  private ticker: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.ticker = setInterval(() => this.actualizarPermanencia(), 15_000);
  }

  ngOnDestroy(): void {
    if (this.ticker) {
      clearInterval(this.ticker);
    }
  }

  async buscar(): Promise<void> {
    const valor = this.criterio.trim();
    if (!valor) {
      this.store.marcarError('Indica una placa o un código de celda.');
      return;
    }
    try {
      const detalle = await firstValueFrom(
        this.modo === 'placa'
          ? this.api.buscarIngresoActivo(valor, undefined)
          : this.api.buscarIngresoActivo(undefined, valor),
      );
      this.detalle.set(detalle);
      this.actualizarPermanencia();
      this.store.limpiarAviso();
    } catch (error) {
      this.detalle.set(null);
      this.store.marcarError(mensajeApi(error));
    }
  }

  async registrarSalida(): Promise<void> {
    const registro = this.detalle()?.registroActivo;
    if (!registro) {
      return;
    }
    this.enviando.set(true);
    try {
      const resultado = await firstValueFrom(this.api.registrarSalida(registro.idRegistro));
      await this.store.refrescarDashboard();
      const tiempo = calcularPermanencia(registro.fechaIngreso);
      this.store.marcarOk(
        `Salida registrada. Celda ${this.detalle()?.celda?.codigo} liberada. Permanencia: ${tiempo.texto}.`,
      );
      this.detalle.set(null);
      this.criterio = '';
      void resultado;
    } catch (error) {
      this.store.marcarError(mensajeApi(error));
    } finally {
      this.enviando.set(false);
    }
  }

  private actualizarPermanencia(): void {
    const ingreso = this.detalle()?.registroActivo?.fechaIngreso;
    if (ingreso) {
      this.permanencia.set(calcularPermanencia(ingreso));
    }
  }
}

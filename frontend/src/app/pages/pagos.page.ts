import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { VehiculoEstadoCuenta } from '../models/parking.models';
import { ApiService } from '../services/api.service';
import { ParkingStore } from '../services/parking.store';
import { formatFecha, formatTarifa, mensajeApi } from '../utils/formatters';

@Component({
  selector: 'app-pagos-page',
  imports: [FormsModule],
  templateUrl: './pagos.page.html',
})
export class PagosPage {
  private readonly api = inject(ApiService);
  protected readonly store = inject(ParkingStore);
  protected readonly formatFecha = formatFecha;
  protected readonly formatTarifa = formatTarifa;

  placaBusqueda = '';
  resultadoVehiculo = signal<VehiculoEstadoCuenta | null>(null);
  enviando = signal(false);

  async buscarVehiculo(): Promise<void> {
    const placa = this.placaBusqueda.trim().toUpperCase();
    if (!placa) {
      this.store.marcarError('Ingrese una placa válida para buscar.');
      return;
    }
    this.enviando.set(true);
    try {
      const res = await firstValueFrom(this.api.consultarVehiculoPlaca(placa));
      this.resultadoVehiculo.set(res);
      this.store.limpiarAviso();
    } catch (err) {
      this.resultadoVehiculo.set(null);
      this.store.marcarError(mensajeApi(err));
    } finally {
      this.enviando.set(false);
    }
  }

  async registrarPagoPresencial(vehiculo: VehiculoEstadoCuenta): Promise<void> {
    this.enviando.set(true);
    try {
      const operarioId = this.store.dashboard()?.defaultOperarioId;
      await firstValueFrom(this.api.registrarPagoPresencial({ placa: vehiculo.placa, id_operario: operarioId }));
      const res = await firstValueFrom(this.api.consultarVehiculoPlaca(vehiculo.placa));
      this.resultadoVehiculo.set(res);
      this.store.marcarOk(`¡Pago presencial registrado correctamente para ${vehiculo.placa}! Mensualidad al día.`);
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
    } finally {
      this.enviando.set(false);
    }
  }
}

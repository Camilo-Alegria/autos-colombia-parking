import { Component, inject, signal } from '@angular/core';

import { CeldaDetalle } from '../models/parking.models';
import { ParkingStore } from '../services/parking.store';
import { formatFecha, formatTarifa } from '../utils/formatters';

@Component({
  selector: 'app-dashboard-page',
  templateUrl: './dashboard.page.html',
})
export class DashboardPage {
  protected readonly store = inject(ParkingStore);
  protected readonly seleccion = signal<CeldaDetalle | null>(null);
  protected readonly formatFecha = formatFecha;
  protected readonly formatTarifa = formatTarifa;

  seleccionar(celda: CeldaDetalle): void {
    this.seleccion.set(celda);
  }

  cerrarPanel(): void {
    this.seleccion.set(null);
  }
}

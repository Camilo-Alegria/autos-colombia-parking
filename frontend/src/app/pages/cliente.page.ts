import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { ClienteEstadoCuenta, VehiculoEstadoCuenta } from '../models/parking.models';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';
import { ParkingStore } from '../services/parking.store';
import { formatFecha, formatTarifa, mensajeApi } from '../utils/formatters';

@Component({
  selector: 'app-cliente-page',
  imports: [FormsModule],
  templateUrl: './cliente.page.html',
})
export class ClientePage implements OnInit {
  private readonly api = inject(ApiService);
  private readonly auth = inject(AuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  protected readonly store = inject(ParkingStore);
  protected readonly formatFecha = formatFecha;
  protected readonly formatTarifa = formatTarifa;

  estadoCuenta = signal<ClienteEstadoCuenta | null>(null);
  cargando = signal(true);
  enviando = signal(false);

  ngOnInit(): void {
    void this.procesarPagoCallback();
  }

  async procesarPagoCallback(): Promise<void> {
    const params = this.route.snapshot.queryParams;
    if (params['status'] === 'approved' && params['payment_id'] && params['external_reference']) {
      try {
        await firstValueFrom(this.api.confirmarPagoOnline(params['external_reference'], params['payment_id']));
        this.store.marcarOk('¡Pago en línea procesado correctamente!');
        void this.router.navigate(['/cliente'], { replaceUrl: true });
      } catch (err) {
        this.store.marcarError(mensajeApi(err));
      }
    }
    await this.cargarEstadoCuenta();
  }

  async cargarEstadoCuenta(): Promise<void> {
    this.cargando.set(true);
    try {
      const cedula = this.auth.usuario()?.documento;
      const res = await firstValueFrom(this.api.obtenerEstadoCuentaCliente(cedula));
      this.estadoCuenta.set(res);
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
    } finally {
      this.cargando.set(false);
    }
  }

  async pagarEnLinea(vehiculo: VehiculoEstadoCuenta): Promise<void> {
    this.enviando.set(true);
    try {
      const res = await firstValueFrom(this.api.crearPreferenciaPago(vehiculo.placa));
      window.location.href = res.init_point;
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
      this.enviando.set(false);
    }
  }
}


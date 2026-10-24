import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { Celda, VehiculoDetalle } from '../models/parking.models';
import { ApiService } from '../services/api.service';
import { ParkingStore } from '../services/parking.store';
import { mensajeApi } from '../utils/formatters';

@Component({
  selector: 'app-editar-page',
  imports: [FormsModule],
  templateUrl: './editar.page.html',
})
export class EditarPage {
  private readonly api = inject(ApiService);
  protected readonly store = inject(ParkingStore);

  placa = '';
  detalle = signal<VehiculoDetalle | null>(null);
  celdasLibres = signal<Celda[]>([]);
  idNuevaCelda: number | null = null;
  enviando = signal(false);

  nombre = '';
  documento = '';
  telefono = '';
  correo = '';
  marca = '';
  color = '';
  placaEdit = '';

  async buscar(): Promise<void> {
    const placa = this.placa.trim().toUpperCase();
    if (!placa) {
      this.store.marcarError('Escribe la placa del suscriptor.');
      return;
    }
    try {
      const detalle = await firstValueFrom(this.api.buscarPorPlaca(placa));
      this.detalle.set(detalle);
      this.nombre = detalle.cliente.nombre;
      this.documento = detalle.cliente.documento;
      this.telefono = detalle.cliente.telefono;
      this.correo = detalle.cliente.correo;
      this.marca = detalle.vehiculo.marca;
      this.color = detalle.vehiculo.color;
      this.placaEdit = detalle.vehiculo.placa;
      this.idNuevaCelda = null;
      this.celdasLibres.set(
        detalle.registroActivo
          ? await firstValueFrom(this.api.celdasDisponibles(detalle.tipo.idTipo))
          : [],
      );
      this.store.limpiarAviso();
    } catch (error) {
      this.detalle.set(null);
      this.store.marcarError(mensajeApi(error));
    }
  }

  async guardarSuscriptor(): Promise<void> {
    const detalle = this.detalle();
    if (!detalle) {
      return;
    }
    this.enviando.set(true);
    try {
      await firstValueFrom(
        this.api.actualizarCliente(detalle.cliente.idCliente, {
          nombre: this.nombre,
          documento: this.documento,
          telefono: this.telefono,
          correo: this.correo,
        }),
      );
      await firstValueFrom(
        this.api.actualizarVehiculo(detalle.vehiculo.idVehiculo, {
          placa: this.placaEdit.trim().toUpperCase(),
          marca: this.marca,
          color: this.color,
          idCliente: detalle.cliente.idCliente,
          idTipo: detalle.vehiculo.idTipo,
        }),
      );
      this.placa = this.placaEdit.trim().toUpperCase();
      await this.buscar();
      await this.store.refrescarDashboard();
      this.store.marcarOk('Suscriptor actualizado.');
    } catch (error) {
      this.store.marcarError(mensajeApi(error));
    } finally {
      this.enviando.set(false);
    }
  }

  async reasignar(): Promise<void> {
    const detalle = this.detalle();
    if (!detalle?.registroActivo) {
      this.store.marcarError('El vehículo no está ingresado; no hay celda para reasignar.');
      return;
    }
    if (!this.idNuevaCelda) {
      this.store.marcarError('Selecciona la nueva celda disponible.');
      return;
    }
    this.enviando.set(true);
    try {
      await firstValueFrom(this.api.reasignarCelda(detalle.registroActivo.idRegistro, this.idNuevaCelda));
      await this.store.refrescarDashboard();
      await this.buscar();
      this.store.marcarOk('Vehículo reasignado a la nueva celda.');
    } catch (error) {
      this.store.marcarError(mensajeApi(error));
    } finally {
      this.enviando.set(false);
    }
  }
}

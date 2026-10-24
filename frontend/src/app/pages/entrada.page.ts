import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { Celda, SuscriptorCreate, VehiculoDetalle } from '../models/parking.models';
import { ApiService } from '../services/api.service';
import { ParkingStore } from '../services/parking.store';
import { formatTarifa, mensajeApi } from '../utils/formatters';

@Component({
  selector: 'app-entrada-page',
  imports: [FormsModule],
  templateUrl: './entrada.page.html',
})
export class EntradaPage implements OnInit {
  private readonly api = inject(ApiService);
  protected readonly store = inject(ParkingStore);
  protected readonly formatTarifa = formatTarifa;

  placa = '';
  idCelda: number | null = null;
  ocupado = signal(false);
  detalle = signal<VehiculoDetalle | null>(null);
  celdasLibres = signal<Celda[]>([]);
  modalAbierto = signal(false);
  enviando = signal(false);

  nuevo: SuscriptorCreate = this.formularioVacio();

  ngOnInit(): void {
    if (!this.store.dashboard()) {
      void this.store.cargarTodo();
    }
  }

  async buscar(): Promise<void> {
    const placa = this.placa.trim().toUpperCase();
    if (!placa) {
      this.store.marcarError('Escribe una placa para buscar.');
      return;
    }
    this.ocupado.set(true);
    this.detalle.set(null);
    this.idCelda = null;
    try {
      const detalle = await firstValueFrom(this.api.buscarPorPlaca(placa));
      this.detalle.set(detalle);
      if (detalle.registroActivo) {
        this.store.marcarError(`El vehículo ${detalle.vehiculo.placa} ya está ingresado en ${detalle.celda?.codigo}.`);
        this.celdasLibres.set([]);
      } else {
        this.store.limpiarAviso();
        await this.cargarCeldas(detalle.tipo.idTipo);
      }
    } catch (error) {
      const http = error as { status?: number };
      if (http.status === 404) {
        this.nuevo = { ...this.formularioVacio(), placa };
        this.modalAbierto.set(true);
      } else {
        this.store.marcarError(mensajeApi(error));
      }
    } finally {
      this.ocupado.set(false);
    }
  }

  async registrarNuevo(): Promise<void> {
    this.enviando.set(true);
    try {
      const creado = await firstValueFrom(
        this.api.registrarSuscriptor({
          ...this.nuevo,
          placa: this.nuevo.placa.trim().toUpperCase(),
          idTipo: Number(this.nuevo.idTipo),
        }),
      );
      this.modalAbierto.set(false);
      this.placa = creado.vehiculo.placa;
      this.detalle.set(creado);
      await this.cargarCeldas(creado.tipo.idTipo);
      await this.store.refrescarDashboard();
      this.store.marcarOk(`Suscriptor ${creado.cliente.nombre} y vehículo ${creado.vehiculo.placa} registrados.`);
    } catch (error) {
      this.store.marcarError(mensajeApi(error));
    } finally {
      this.enviando.set(false);
    }
  }

  async registrarEntrada(): Promise<void> {
    const detalle = this.detalle();
    const operarioId = this.store.dashboard()?.defaultOperarioId;
    if (!detalle) {
      this.store.marcarError('Busca primero un vehículo.');
      return;
    }
    if (!operarioId) {
      this.store.marcarError('No hay un operario configurado en el backend.');
      return;
    }
    if (!this.idCelda) {
      this.store.marcarError('Selecciona una celda libre.');
      return;
    }
    this.enviando.set(true);
    try {
      await firstValueFrom(
        this.api.registrarIngreso({
          idVehiculo: detalle.vehiculo.idVehiculo,
          idOperario: operarioId,
          idCelda: this.idCelda,
        }),
      );
      await this.store.refrescarDashboard();
      this.store.marcarOk(`Entrada registrada para ${detalle.vehiculo.placa}.`);
      this.detalle.set(null);
      this.celdasLibres.set([]);
      this.placa = '';
      this.idCelda = null;
    } catch (error) {
      this.store.marcarError(mensajeApi(error));
    } finally {
      this.enviando.set(false);
    }
  }

  cerrarModal(): void {
    this.modalAbierto.set(false);
  }

  private async cargarCeldas(idTipo: number): Promise<void> {
    this.celdasLibres.set(await firstValueFrom(this.api.celdasDisponibles(idTipo)));
  }

  private formularioVacio(): SuscriptorCreate {
    return {
      nombre: '',
      documento: '',
      telefono: '',
      correo: '',
      placa: '',
      marca: '',
      color: '',
      idTipo: this.store.tipos()[0]?.idTipo ?? 1,
    };
  }
}

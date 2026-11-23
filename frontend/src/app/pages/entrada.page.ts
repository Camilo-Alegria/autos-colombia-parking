import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { Router } from '@angular/router';
import { VehiculoEstadoCuenta } from '../models/parking.models';
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
  private readonly router = inject(Router);
  protected readonly store = inject(ParkingStore);
  protected readonly formatTarifa = formatTarifa;

  placa = '';
  idCelda: number | null = null;
  ocupado = signal(false);
  detalle = signal<VehiculoDetalle | null>(null);
  celdasLibres = signal<Celda[]>([]);
  modalAbierto = signal(false);
  vehiculoEstado = signal<VehiculoEstadoCuenta | null>(null);
  enviando = signal(false);

  nuevo: SuscriptorCreate = this.formularioVacio();
  clienteInfo = signal<{ existe: boolean; nombre: string; telefono: string } | null>(null);
  clienteExistente = signal(false);

  async buscarPropietario(): Promise<void> {
    const cedula = this.nuevo.documento.trim();
    if (!cedula) return;
    try {
      const info = await firstValueFrom(this.api.consultarPropietario(cedula));
      this.clienteInfo.set(info);
      this.clienteExistente.set(info.existe);
      if (info.existe) {
        this.nuevo.nombre = info.nombre;
        this.nuevo.telefono = info.telefono;
        this.nuevo.password = '**********';
      }
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
    }
  }


  ngOnInit(): void {
    if (!this.store.dashboard()) {
      void this.store.cargarTodo();
    }
  }

  abrirModalRegistro(): void {
    this.nuevo = { ...this.formularioVacio(), placa: this.placa.trim().toUpperCase() };
    this.modalAbierto.set(true);
  }

  async buscar(): Promise<void> {
    const placa = this.placa.trim().toUpperCase();
    if (!placa) {
      this.store.marcarError('Escribe una placa para buscar.');
      return;
    }
    this.ocupado.set(true);
    this.detalle.set(null);
    this.vehiculoEstado.set(null);
    this.idCelda = null;
    try {
      const [detalle, estadoVeh] = await Promise.all([
        firstValueFrom(this.api.buscarPorPlaca(placa)),
        firstValueFrom(this.api.consultarVehiculoPlaca(placa)).catch(() => null),
      ]);
      this.detalle.set(detalle);
      this.vehiculoEstado.set(estadoVeh);

      const semaforo = estadoVeh?.estado_semaforo;
      if (semaforo === 'SE_REQUIERE_PAGO' || detalle.vehiculo.estado_pago === 'PENDIENTE') {
        this.store.marcarError(`INGRESO BLOQUEADO: Mensualidad vencida — Se requiere pago para el vehículo ${placa}.`);
        this.celdasLibres.set([]);
      } else if (detalle.registroActivo) {
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
      const payload = {
        cedula: this.nuevo.documento.trim(),
        nombre: this.nuevo.nombre.trim(),
        telefono: this.nuevo.telefono.trim(),
        password: this.nuevo.password || 'cliente123',
        placa: this.nuevo.placa.trim().toUpperCase(),
        idTipo: Number(this.nuevo.idTipo),
        marca: this.nuevo.marca.trim(),
        modelo: this.nuevo.modelo.trim(),
        color: this.nuevo.color.trim(),
      };
      const creado = await firstValueFrom(this.api.registrarVehiculoCliente(payload));
      this.modalAbierto.set(false);
      this.placa = creado.placa;
      await this.buscar();
      await this.store.refrescarDashboard();
      this.store.marcarOk(`Cliente ${this.nuevo.nombre} registrado. Corte: día ${creado.dia_corte}.`);
    } catch (error) {
      this.store.marcarError(mensajeApi(error));
    } finally {
      this.enviando.set(false);
    }
  }

  async registrarEntrada(): Promise<void> {
    const detalle = this.detalle();
    const estadoVeh = this.vehiculoEstado();
    const operarioId = this.store.dashboard()?.defaultOperarioId;
    if (!detalle) {
      this.store.marcarError('Busca primero un vehículo.');
      return;
    }
    if (estadoVeh?.estado_semaforo === 'SE_REQUIERE_PAGO' || detalle.vehiculo.estado_pago === 'PENDIENTE') {
      this.store.marcarError('INGRESO BLOQUEADO: Mensualidad vencida — Se requiere pago.');
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
      this.vehiculoEstado.set(null);
      this.celdasLibres.set([]);
      this.placa = '';
      this.idCelda = null;
    } catch (error) {
      const http = error as { status?: number };
      if (http.status === 403) {
        this.store.marcarError('INGRESO BLOQUEADO: Mensualidad vencida — Se requiere pago.');
      } else {
        this.store.marcarError(mensajeApi(error));
      }
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

  irAPagos(): void {
    void this.router.navigate(['/pagos']);
  }

  private formularioVacio(): SuscriptorCreate {
    return {
      nombre: '',
      documento: '',
      telefono: '',
      correo: '',
      placa: '',
      marca: '',
      modelo: '',
      color: '',
      estado_pago: 'AL_DIA',
      idTipo: this.store.tipos()[0]?.idTipo ?? 1,
    };
  }
}

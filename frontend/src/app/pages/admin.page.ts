import { HttpClient } from '@angular/common/http';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';

import { Auditoria, Celda, Usuario, VehiculoDetalle } from '../models/parking.models';
import { ApiService } from '../services/api.service';
import { ParkingStore } from '../services/parking.store';
import { formatFecha, mensajeApi } from '../utils/formatters';

@Component({
  selector: 'app-admin-page',
  imports: [FormsModule],
  templateUrl: './admin.page.html',
})
export class AdminPage implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiService);
  protected readonly store = inject(ParkingStore);
  protected readonly formatFecha = formatFecha;

  subTab: 'usuarios' | 'celdas' | 'vehiculos' | 'auditoria' = 'usuarios';

  usuarios = signal<Usuario[]>([]);
  celdas = signal<Celda[]>([]);
  auditorias = signal<Auditoria[]>([]);

  nuevoOperario = { nombre: '', documento: '', usuario: '', password: '', rol: 'OPERADOR', activo: true };
  nuevaCelda = { codigo: '', idTipo: 1, estado: 'LIBRE', activo: true };

  placaBusqueda = '';
  detalleVehiculo = signal<VehiculoDetalle | null>(null);
  editCliente = { nombre: '', documento: '', telefono: '', correo: '' };
  editVehiculo = { placa: '', marca: '', modelo: '', color: '', estado_pago: 'AL_DIA', idCliente: 0, idTipo: 1 };
  enviando = signal(false);

  ngOnInit(): void {
    void this.cargarDatosAdmin();
  }

  async cargarDatosAdmin(): Promise<void> {
    try {
      const [u, c, a] = await Promise.all([
        firstValueFrom(this.http.get<Usuario[]>('/api/usuarios/')),
        firstValueFrom(this.http.get<Celda[]>('/api/celdas/')),
        firstValueFrom(this.http.get<Auditoria[]>('/api/auditoria/')),
      ]);
      this.usuarios.set(u);
      this.celdas.set(c);
      this.auditorias.set(a);
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
    }
  }

  async crearUsuario(): Promise<void> {
    const nombre = (this.nuevoOperario.nombre || '').trim();
    const documento = (this.nuevoOperario.documento || '').trim();
    const usuario = (this.nuevoOperario.usuario || '').trim();
    const password = (this.nuevoOperario.password || '').trim();
    const rol = (this.nuevoOperario.rol || '').trim();

    if (!nombre) {
      this.store.marcarError('El campo Nombre completo es obligatorio');
      return;
    }
    if (!documento) {
      this.store.marcarError('El campo Documento es obligatorio');
      return;
    }
    if (!usuario) {
      this.store.marcarError('El campo Usuario es obligatorio');
      return;
    }
    if (!password) {
      this.store.marcarError('El campo Contraseña es obligatorio');
      return;
    }
    if (!rol) {
      this.store.marcarError('El campo Rol es obligatorio');
      return;
    }

    const payload = {
      ...this.nuevoOperario,
      nombre,
      documento,
      usuario,
      password,
      rol: rol.toUpperCase(),
    };

    try {
      await firstValueFrom(this.http.post('/api/usuarios/', payload));
      this.nuevoOperario = { nombre: '', documento: '', usuario: '', password: '', rol: 'OPERADOR', activo: true };
      await this.cargarDatosAdmin();
      this.store.marcarOk('Operador creado correctamente.');
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
    }
  }

  async desactivarUsuario(id: number): Promise<void> {
    if (!confirm('¿Desactivar (borrado lógico) este usuario?')) return;
    try {
      await firstValueFrom(this.http.delete(`/api/usuarios/${id}`));
      await this.cargarDatosAdmin();
      this.store.marcarOk('Usuario desactivado.');
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
    }
  }

  async crearCelda(): Promise<void> {
    const codigo = (this.nuevaCelda.codigo || '').trim().toUpperCase();
    const idTipo = Number(this.nuevaCelda.idTipo);

    if (!codigo) {
      this.store.marcarError('El código de la celda es obligatorio');
      return;
    }
    if (!idTipo || isNaN(idTipo) || idTipo <= 0) {
      this.store.marcarError('Debe seleccionar un tipo de vehículo');
      return;
    }

    try {
      await firstValueFrom(this.http.post('/api/celdas/', {
        ...this.nuevaCelda,
        codigo,
        idTipo,
      }));
      this.nuevaCelda = { codigo: '', idTipo: 1, estado: 'LIBRE', activo: true };
      await this.cargarDatosAdmin();
      await this.store.refrescarDashboard();
      this.store.marcarOk('Celda creada.');
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
    }
  }

  async eliminarCelda(celda: Celda, event: Event): Promise<void> {
    event.stopPropagation();
    if (!confirm(`¿Estás seguro de eliminar la celda ${celda.codigo}?`)) return;
    try {
      await firstValueFrom(this.api.eliminarCelda(celda.idCelda));
      await this.cargarDatosAdmin();
      await this.store.refrescarDashboard();
      this.store.marcarOk(`Celda ${celda.codigo} eliminada correctamente.`);
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
    }
  }

  async buscarVehiculoAdmin(): Promise<void> {
    const placa = this.placaBusqueda.trim().toUpperCase();
    if (!placa) return;
    try {
      const det = await firstValueFrom(this.api.buscarPorPlaca(placa));
      this.detalleVehiculo.set(det);
      this.editCliente = { ...det.cliente };
      this.editVehiculo = {
        placa: det.vehiculo.placa,
        marca: det.vehiculo.marca,
        modelo: det.vehiculo.modelo ?? '',
        color: det.vehiculo.color,
        estado_pago: det.vehiculo.estado_pago ?? 'AL_DIA',
        idCliente: det.cliente.idCliente,
        idTipo: det.tipo.idTipo,
      };
      this.store.limpiarAviso();
    } catch (err) {
      this.detalleVehiculo.set(null);
      this.store.marcarError(mensajeApi(err));
    }
  }

  async guardarEdicionAdmin(): Promise<void> {
    const det = this.detalleVehiculo();
    if (!det) return;
    this.enviando.set(true);
    try {
      await firstValueFrom(this.api.actualizarCliente(det.cliente.idCliente, this.editCliente));
      await firstValueFrom(this.api.actualizarVehiculo(det.vehiculo.idVehiculo, {
        ...this.editVehiculo,
        placa: this.editVehiculo.placa.trim().toUpperCase(),
      }));
      await this.store.refrescarDashboard();
      await this.cargarDatosAdmin();
      this.store.marcarOk('Datos actualizados por Administrador.');
    } catch (err) {
      this.store.marcarError(mensajeApi(err));
    } finally {
      this.enviando.set(false);
    }
  }
}

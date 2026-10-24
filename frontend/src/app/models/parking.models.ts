export interface ClienteResumen {
  idCliente: number;
  nombre: string;
  documento: string;
  telefono: string;
  correo: string;
}

export interface TipoResumen {
  idTipo: number;
  nombre: string;
  tarifa: number;
}

export interface VehiculoResumen {
  idVehiculo: number;
  placa: string;
  marca: string;
  color: string;
  idCliente: number;
  idTipo: number;
}

export interface RegistroResumen {
  idRegistro: number;
  fechaIngreso: string;
  fechaSalida: string | null;
  estadoRegistro: string;
  tiempoParqueo: number;
  idVehiculo: number;
  idCelda: number;
  idOperario: number;
}

export interface CeldaDetalle {
  idCelda: number;
  codigo: string;
  estado: string;
  idTipo: number;
  tipo: TipoResumen | null;
  registro: RegistroResumen | null;
  vehiculo: VehiculoResumen | null;
  cliente: ClienteResumen | null;
}

export interface Dashboard {
  vehiculosRegistrados: number;
  vehiculosIngresados: number;
  celdasDisponibles: number;
  defaultOperarioId: number | null;
  celdas: CeldaDetalle[];
}

export interface VehiculoDetalle {
  vehiculo: VehiculoResumen;
  cliente: ClienteResumen;
  tipo: TipoResumen;
  celda: CeldaDetalle | null;
  registroActivo: RegistroResumen | null;
}

export interface Celda {
  idCelda: number;
  codigo: string;
  estado: string;
  idTipo: number;
}

export interface Tipo {
  idTipo: number;
  nombre: string;
  descripcion: string | null;
  tarifa: number;
}

export interface SuscriptorCreate {
  nombre: string;
  documento: string;
  telefono: string;
  correo: string;
  placa: string;
  marca: string;
  color: string;
  idTipo: number;
}

export interface IngresoCreate {
  idVehiculo: number;
  idOperario: number;
  idCelda?: number | null;
}

export interface ClienteUpdate {
  nombre: string;
  documento: string;
  telefono: string;
  correo: string;
}

export interface VehiculoUpdate {
  placa: string;
  marca: string;
  color: string;
  idCliente: number;
  idTipo: number;
}

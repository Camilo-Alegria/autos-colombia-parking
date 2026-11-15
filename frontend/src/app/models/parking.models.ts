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
  modelo: string;
  color: string;
  estado_pago: string;
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
  activo: boolean;
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
  activo: boolean;
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
  modelo: string;
  color: string;
  estado_pago: string;
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
  modelo: string;
  color: string;
  estado_pago: string;
  idCliente: number;
  idTipo: number;
}

export interface Usuario {
  id_usuario: number;
  nombre: string;
  documento: string;
  usuario: string;
  rol: string;
  activo: boolean;
}

export interface UsuarioCreate {
  nombre: string;
  documento: string;
  usuario: string;
  password: string;
  rol: string;
  activo: boolean;
}

export interface UsuarioUpdate {
  nombre?: string;
  documento?: string;
  usuario?: string;
  password?: string;
  rol?: string;
  activo?: boolean;
}

export interface Auditoria {
  id: number;
  fecha_hora: string;
  usuario_id: number | null;
  usuario_nombre: string | null;
  accion: string;
  detalles: string | null;
  ip: string | null;
}

export interface LoginRequest {
  usuario: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  id_usuario: number;
  nombre: string;
  usuario: string;
  rol: string;
}


import { Injectable, inject } from '@angular/core';
import { ParkingStore } from './parking.store';

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private readonly store = inject(ParkingStore);
  private socket: WebSocket | null = null;

  conectar(): void {
    if (this.socket) return;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/celdas`;
    try {
      this.socket = new WebSocket(wsUrl);
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === 'celda_actualizada') {
            void this.store.refrescarDashboard();
          }
        } catch {}
      };
      this.socket.onclose = () => {
        this.socket = null;
        setTimeout(() => this.conectar(), 5000);
      };
    } catch {
      setTimeout(() => this.conectar(), 5000);
    }
  }
}

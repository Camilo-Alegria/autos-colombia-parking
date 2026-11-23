import { Component, inject, OnInit } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { LoginPage } from '../pages/login.page';
import { AuthService } from '../services/auth.service';
import { ParkingStore } from '../services/parking.store';
import { WebSocketService } from '../services/websocket.service';

@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, LoginPage],
  templateUrl: './shell.html',
})
export class Shell implements OnInit {
  protected readonly store = inject(ParkingStore);
  protected readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly ws = inject(WebSocketService);

  async ngOnInit(): Promise<void> {
    await this.auth.cargarUsuarioActual();
    if (this.auth.isClient()) {
      if (this.router.url !== '/cliente') {
        void this.router.navigate(['/cliente']);
      }
    } else {
      void this.store.cargarTodo();
      this.ws.conectar();
    }
  }
}



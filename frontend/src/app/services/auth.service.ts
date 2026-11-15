import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { LoginRequest, TokenResponse, Usuario } from '../models/parking.models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api';

  readonly token = signal<string | null>(localStorage.getItem('token'));
  readonly usuario = signal<Usuario | null>(null);

  readonly isAuthenticated = computed(() => !!this.token());
  readonly isAdmin = computed(() => this.usuario()?.rol === 'ADMINISTRADOR');
  readonly isOperator = computed(() => this.usuario()?.rol === 'OPERADOR' || this.isAdmin());

  async login(payload: LoginRequest): Promise<void> {
    const res = await firstValueFrom(this.http.post<TokenResponse>(`${this.base}/auth/login`, payload));
    localStorage.setItem('token', res.access_token);
    this.token.set(res.access_token);
    await this.cargarUsuarioActual();
  }

  async cargarUsuarioActual(): Promise<void> {
    if (!this.token()) return;
    try {
      const u = await firstValueFrom(this.http.get<Usuario>(`${this.base}/auth/me`));
      this.usuario.set(u);
    } catch {
      this.logout();
    }
  }

  async logout(): Promise<void> {
    const currentToken = this.token();
    if (currentToken) {
      try {
        await firstValueFrom(this.http.post(`${this.base}/auth/logout`, {}));
      } catch {
        // En caso de fallo o si el token ya expiró, continuar limpiando el almacenamiento local
      }
    }
    localStorage.removeItem('token');
    this.token.set(null);
    this.usuario.set(null);
  }
}

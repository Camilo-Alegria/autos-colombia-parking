import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';

import { LoginRequest, TokenResponse, Usuario } from '../models/parking.models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl.replace('/api', '');

  readonly token = signal<string | null>(localStorage.getItem('token'));
  readonly usuario = signal<Usuario | null>(null);

  readonly isAuthenticated = computed(() => !!this.token());
  readonly isAdmin = computed(() => this.usuario()?.rol === 'ADMINISTRADOR');
  readonly isOperator = computed(() => this.usuario()?.rol === 'OPERADOR' || this.isAdmin());
  readonly isClient = computed(() => this.usuario()?.rol === 'CLIENTE');

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
      }
    }
    localStorage.removeItem('token');
    this.token.set(null);
    this.usuario.set(null);
  }
}



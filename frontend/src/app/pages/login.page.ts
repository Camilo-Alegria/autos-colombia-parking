import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../services/auth.service';
import { mensajeApi } from '../utils/formatters';

@Component({
  selector: 'app-login-page',
  imports: [FormsModule],
  templateUrl: './login.page.html',
})
export class LoginPage {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  usuario = '';
  password = '';
  cargando = signal(false);
  error = signal<string | null>(null);

  async ingresar(): Promise<void> {
    if (!this.usuario.trim() || !this.password) {
      this.error.set('Ingresa usuario y contraseña.');
      return;
    }
    this.cargando.set(true);
    this.error.set(null);
    try {
      await this.auth.login({ usuario: this.usuario.trim(), password: this.password });
      
      if (this.auth.isClient()) {
        void this.router.navigate(['/cliente']);
      } else {
        void this.router.navigate(['/dashboard']);
      }
    } catch (err) {
      this.error.set(mensajeApi(err));
    } finally {
      this.cargando.set(false);
    }
  }
}


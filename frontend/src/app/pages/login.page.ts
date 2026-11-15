import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AuthService } from '../services/auth.service';
import { mensajeApi } from '../utils/formatters';

@Component({
  selector: 'app-login-page',
  imports: [FormsModule],
  templateUrl: './login.page.html',
})
export class LoginPage {
  private readonly auth = inject(AuthService);
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
    } catch (err) {
      this.error.set(mensajeApi(err));
    } finally {
      this.cargando.set(false);
    }
  }
}

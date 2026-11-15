import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class CeldasService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api/celdas';

  eliminarCelda(idCelda: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${idCelda}`);
  }
}

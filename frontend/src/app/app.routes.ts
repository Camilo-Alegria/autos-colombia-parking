import { Routes } from '@angular/router';

import { Shell } from './layout/shell';
import { DashboardPage } from './pages/dashboard.page';
import { EditarPage } from './pages/editar.page';
import { EntradaPage } from './pages/entrada.page';
import { SalidaPage } from './pages/salida.page';

export const routes: Routes = [
  {
    path: '',
    component: Shell,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardPage },
      { path: 'entrada', component: EntradaPage },
      { path: 'salida', component: SalidaPage },
      { path: 'editar', component: EditarPage },
    ],
  },
];

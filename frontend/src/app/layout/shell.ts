import { Component, inject, OnInit } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { ParkingStore } from '../services/parking.store';

@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './shell.html',
})
export class Shell implements OnInit {
  protected readonly store = inject(ParkingStore);

  ngOnInit(): void {
    void this.store.cargarTodo();
  }
}
